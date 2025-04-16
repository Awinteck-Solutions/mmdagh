from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from .models import Billing, Rate, Payment, RevenueTarget, AccumulatedOwing
from accounts.models import DataCapture ,UserAssignment
from .forms import PaymentForm
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from decimal import Decimal
from billing.models import BillingAudit
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from accounts.models import Region, MMDA, DataCapture  # Import required models
import pandas as pd
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.timezone import make_naive
from django.shortcuts import get_object_or_404, render
from decimal import Decimal
from django.http import JsonResponse
import logging
from django.db.models import Avg, Count, Sum, Max, Min
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseForbidden
import csv
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.functions import ExtractYear, Coalesce
from .models import CustomerStatement
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
import logging
import json
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site



logger = logging.getLogger(__name__)


# Bill Generation

def generate_bill(request, account_id):
    account = get_object_or_404(DataCapture, id=account_id)

    # Determine the current accounting year
    current_year = datetime.now().year

    # Check if a bill already exists for this account
    existing_bill = Billing.objects.filter(
        ghana_card=account.ghana_card
    ).first()

    if existing_bill:
        return JsonResponse({
            'status': 'error',
            'message': f"A bill already exists for the account with Ghana Card: {account.ghana_card}. Please review the existing bill."
        }, status=400)

    # Calculate brought forward (B/F) from unpaid bills of the previous year
    previous_year = current_year - 1
    previous_bills = Billing.objects.filter(account=account, accounting_year=previous_year)
    brought_forward = sum(bill.closing_balance for bill in previous_bills if bill.closing_balance > 0)

    # Fetch the rate and calculate total amount
    try:
        rate = Rate.objects.get(category=account.category)
        total_amount = rate.rate * account.rooms
    except Rate.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': "Error: Rate for the given category does not exist."}, status=404)
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': "Error: Unable to calculate the bill due to invalid input."}, status=400)

    # Calculate the current year bill as the total amount
    current_year_bill = total_amount

    # Calculate total due as the sum of brought forward and current year bill
    total_due = current_year_bill + brought_forward

    # Create a new Billing record within a transaction
    try:
        with transaction.atomic():
            billing = Billing.objects.create(
                account=account,
                name_mmda="AMASAMAN MUNICIPAL ASSEMBLY",
                ghana_card=account.ghana_card,
                recipient_name=f"{account.first_name} {account.surname}",
                address=account.street_name,
                contact_number=account.contact_1,
                gps_address=account.gps_address,
                rooms=account.rooms,
                payment_option="full",
                accounting_year=current_year,
                brought_forward=brought_forward,
                amount=current_year_bill,
                total_due=total_due,
                mmda=account.mmda  # Ensure you are assigning the MMDA here
            )
            billing.calculate_closing_balance()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': f"Bill for {account.first_name} generated successfully!"})

# Year-End Processing View
def year_end_process(request):
    current_year = datetime.now().year

    # Process all bills for the current year
    current_year_bills = Billing.objects.filter(accounting_year=current_year)
    for bill in current_year_bills:
        bill.calculate_closing_balance()

    return HttpResponse(f"Year-end processing for {current_year} completed successfully.")


@login_required
def bill_list(request):
    """
    View to display bills with region and MMDA selection for superusers.
    """
    user = request.user
    bills = Billing.objects.none()  # Start with an empty queryset
    selected_region = None
    selected_mmda = None

    if user.is_superuser:
        regions = Region.objects.all()
        mmdas = MMDA.objects.all()

        selected_region = request.GET.get("region")
        selected_mmda = request.GET.get("mmda")

        if selected_region and selected_mmda:
            assigned_accounts = DataCapture.objects.filter(region_id=selected_region, mmda_id=selected_mmda)
            bills = Billing.objects.filter(account__in=assigned_accounts)
        
    else:
        # Filter based on the user's assigned region and MMDA
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region and MMDA.")

        assigned_accounts = DataCapture.objects.filter(region=user_assignment.region, mmda=user_assignment.mmda)
        bills = Billing.objects.filter(account__in=assigned_accounts)

    context = {
        'bills': bills,
        'regions': regions if user.is_superuser else None,
        'mmdas': mmdas if user.is_superuser else None,
        'selected_region': selected_region,
        'selected_mmda': selected_mmda,
    }

    return render(request, 'billing/bill_list.html', context)

#export to pdf
@login_required
def export_bills_pdf(request):
    """
    Exports the filtered bills to a PDF file.
    """
    selected_region = request.GET.get("region")
    selected_mmda = request.GET.get("mmda")
    
    bills = Billing.objects.all()
    if selected_region and selected_mmda:
        assigned_accounts = DataCapture.objects.filter(region_id=selected_region, mmda_id=selected_mmda)
        bills = Billing.objects.filter(account__in=assigned_accounts)
    
    template_path = 'billing/bills_pdf_template.html'
    context = {'bills': bills}
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bills.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response


#export to excel
def export_bills_excel(request):
    bills = Billing.objects.all().values(
        "id", "recipient_name", "ghana_card", "gps_address", "name_mmda",
        "amount", "total_paid", "closing_balance", "payment_status", "bill_date"
    )

    # Convert queryset to a DataFrame
    df = pd.DataFrame(list(bills))

    # Convert timezone-aware datetime fields to timezone-naive
    if "bill_date" in df.columns:
        df["bill_date"] = df["bill_date"].apply(lambda x: make_naive(x) if pd.notna(x) else x)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="bills.xlsx"'

    df.to_excel(response, index=False, engine='openpyxl')

    return response




# Bill Detail
def bill_detail(request, bill_id=None, ghana_card=None):
    # Try to fetch the billing record using bill_id first
    if bill_id:
        bill = get_object_or_404(Billing, id=bill_id)
    # If bill_id is not provided, try fetching using ghana_card
    elif ghana_card:
        bill = get_object_or_404(Billing, ghana_card=ghana_card)
    else:
        # Handle the case where neither parameter is provided
        return render(request, 'billing/error.html', {'error': 'No bill ID or Ghana Card provided.'})

    amount_left = 0
    if bill.amount is not None and bill.amount_due is not None:
        amount_left = bill.amount - bill.amount_due if bill.amount > bill.amount_due else 0

    return render(request, 'billing/bill_detail.html', {'bill': bill, 'amount_left': amount_left})


def payment_form(request, bill_id):
    billing = get_object_or_404(Billing, id=bill_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.billing = billing
            payment.save()
            logger.info(f"Payment of {payment.amount} for billing ID {bill_id} was successful.")
            return redirect('bill_detail', bill_id=bill_id)
        else:
            logger.warning(f"Payment form for billing ID {bill_id} is invalid: {form.errors}")
    else:
        form = PaymentForm()
    return render(request, 'billing/payment_form.html', {'form': form, 'billing': billing})


@login_required
def revenue_account(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region and MMDA.")

        # Find DataCapture accounts that match the user's region and MMDA
        assigned_accounts = DataCapture.objects.filter(region=user_assignment.region, mmda=user_assignment.mmda)

        if not assigned_accounts.exists():
            return HttpResponseForbidden("No accounts found for your assigned region and MMDA.")

        # Find Billing records linked to those accounts
        assigned_billings = Billing.objects.filter(account__in=assigned_accounts)

        if not assigned_billings.exists():
            return HttpResponseForbidden("No billing records found for your assigned region and MMDA.")

        # Filter payments based on assigned Billing records
        payments = Payment.objects.filter(billing__in=assigned_billings).order_by('-payment_date')

        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0.0
    else:
        payments = Payment.objects.all().order_by('-payment_date')  # Superusers see all data
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0.0  

    context = {
        'payments': payments,
        'total_revenue': total_revenue,
    }
    return render(request, 'billing/revenue_account.html', context)


 
 #Total Revenue
def total_revenue(request):

    # Calculate the total revenue
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Monthly revenue breakdown
    current_year = datetime.now().year
    monthly_revenue = (
        Payment.objects.filter(payment_date__year=current_year)
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    return render(request, 'billing/total_revenue.html', {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
    })


# Unpaid Bills
from accounts.models import Region, MMDA, DataCapture  # Import required models

@login_required
def unpaid_bills(request):
    """
    View to display unpaid bills with region and MMDA selection for superusers.
    """
    user = request.user
    unpaid_bills = Billing.objects.none()  # Start with an empty queryset
    selected_region = None
    selected_mmda = None

    if user.is_superuser:
        regions = Region.objects.all()
        mmdas = MMDA.objects.all()

        selected_region = request.GET.get("region")
        selected_mmda = request.GET.get("mmda")

        if selected_region and selected_mmda:
            assigned_accounts = DataCapture.objects.filter(region_id=selected_region, mmda_id=selected_mmda)
            unpaid_bills = Billing.objects.filter(account__in=assigned_accounts, payment_status__in=['unpaid', 'partly_paid'])
        
    else:
        # Filter based on the user's assigned region and MMDA
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region and MMDA.")

        assigned_accounts = DataCapture.objects.filter(region=user_assignment.region, mmda=user_assignment.mmda)
        unpaid_bills = Billing.objects.filter(account__in=assigned_accounts, payment_status__in=['unpaid', 'partly_paid'])

    # Calculate total unpaid balance
    total_unpaid = unpaid_bills.aggregate(total=Sum('closing_balance'))['total'] or 0.0

    context = {
        'unpaid_bills': unpaid_bills,
        'total_unpaid': total_unpaid,
        'regions': regions if user.is_superuser else None,
        'mmdas': mmdas if user.is_superuser else None,
        'selected_region': selected_region,
        'selected_mmda': selected_mmda,
    }

    return render(request, 'billing/unpaid_bills.html', context)


#export to excel
def export_unpaid_bills_excel (request):
    bills = Billing.objects.all().values(
        "id", "recipient_name", "ghana_card", "gps_address", "name_mmda",
        "amount", "total_paid", "closing_balance", "payment_status", "bill_date"
    )

    # Convert queryset to a DataFrame
    df = pd.DataFrame(list(bills))

    # Convert timezone-aware datetime fields to timezone-naive
    if "bill_date" in df.columns:
        df["bill_date"] = df["bill_date"].apply(lambda x: make_naive(x) if pd.notna(x) else x)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="bills.xlsx"'

    df.to_excel(response, index=False, engine='openpyxl')

    return response

#def export_unpaid_bills_pdf (request):
    #pass



#export to pdf
@login_required
def export_unpaid_bills_pdf(request):
    """
    Exports the filtered bills to a PDF file.
    """
    selected_region = request.GET.get("region")
    selected_mmda = request.GET.get("mmda")
    
    bills = Billing.objects.all()
    if selected_region and selected_mmda:
        assigned_accounts = DataCapture.objects.filter(region_id=selected_region, mmda_id=selected_mmda)
        bills = Billing.objects.filter(account__in=assigned_accounts)
    
    template_path = 'billing/bills_pdf_template.html'
    context = {'bills': bills}
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bills.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response



 #Revenue Summary
'''@login_required
def revenue_summary(request):
    """
    View to display total revenue restricted by the user's region and MMDA.
    """
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region and MMDA.")

        # Get DataCapture accounts matching user’s region and MMDA
        assigned_accounts = DataCapture.objects.filter(region=user_assignment.region, mmda=user_assignment.mmda)

        if not assigned_accounts.exists():
            return HttpResponseForbidden("No accounts found for your assigned region and MMDA.")

        # Get Billing records related to those accounts
        assigned_billings = Billing.objects.filter(account__in=assigned_accounts)

        if not assigned_billings.exists():
            return HttpResponseForbidden("No billing records found for your assigned region and MMDA.")

        # Calculate revenue from payments linked to those billings
        total_revenue = Payment.objects.filter(billing__in=assigned_billings).aggregate(total=Sum('amount'))['total'] or 0.0
    else:
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0.0  # Superusers see all data

    return render(request, 'billing/revenue_summary.html', {'total_revenue': total_revenue})'''


from django.db.models.functions import TruncMonth

def revenue_summary(request):
    user = request.user
    current_year = datetime.now().year

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region and MMDA.")

        assigned_accounts = DataCapture.objects.filter(region=user_assignment.region, mmda=user_assignment.mmda)
        if not assigned_accounts.exists():
            return HttpResponseForbidden("No accounts found for your assigned region and MMDA.")

        assigned_billings = Billing.objects.filter(account__in=assigned_accounts)
        if not assigned_billings.exists():
            return HttpResponseForbidden("No billing records found for your assigned region and MMDA.")

        payments = Payment.objects.filter(billing__in=assigned_billings)

        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0.0
        pending_amount = assigned_billings.aggregate(
            pending=Sum('amount') - Sum('total_paid'))['pending'] or 0.0
        average_payment = payments.aggregate(
            average=Sum('amount') / Count('id'))['average'] or 0.0

        target = RevenueTarget.objects.filter(
            mmda=user_assignment.mmda,
            region=user_assignment.region,
            year=current_year
        ).first()
        revenue_target = target.target if target else 0.0

        recent_payments = payments.order_by('-payment_date')[:5]
        payment_trends = payments.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

    else:
        billings = Billing.objects.all()
        payments = Payment.objects.all()

        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0.0
        pending_amount = billings.aggregate(
            pending=Sum('amount') - Sum('total_paid'))['pending'] or 0.0
        average_payment = payments.aggregate(
            average=Sum('amount') / Count('id'))['average'] or 0.0

        target = RevenueTarget.objects.filter(year=current_year).first()
        revenue_target = target.target if target else 0.0

        recent_payments = payments.order_by('-payment_date')[:5]
        payment_trends = payments.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

    return render(request, 'billing/revenue_summary.html', {
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'revenue_target': revenue_target,
        'average_payment': average_payment,
        'payments': recent_payments,
        'payment_trends': payment_trends,
    })




# Payment Trends Over Time
'''def payment_trends(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        # Filter payments based on assigned region and MMDA
        payment_trends = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
    else:
        payment_trends = Payment.objects.annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')

    return render(request, 'billing/payment_trends.html', {'payment_trends': payment_trends})'''


from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

def payment_trends(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        trends = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
    else:
        trends = Payment.objects.annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')

    # Format data for the chart
    chart_labels = [DateFormat(t['month']).format('M Y') for t in trends]
    chart_data = [float(t['total']) for t in trends]

    return render(request, 'billing/payment_trends.html', {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'payment_trends': trends
    })



#RevenueTarget
def revenue_target(request):
    targets = RevenueTarget.objects.all()
    targets_data = []
    for target in targets:
        total_collected = Payment.objects.filter(payment_date__year=target.year).aggregate(total=Sum('amount'))['total'] or 0
        percentage_achieved = (total_collected / target.target * 100) if target.target > 0 else 0

        targets_data.append({
            'year': target.year,
            'target': target.target,
            'total_collected': total_collected,
            'percentage_achieved': percentage_achieved
        })

    context = {'targets_data': targets_data}
    return render(request, 'revenue_target.html', context)





# Payment Analysis by Category
def payment_analysis_by_category(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        analysis = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).values('billing__category').annotate(total=Sum('amount')).order_by('billing__category')
    else:
        analysis = Payment.objects.values('billing__category').annotate(total=Sum('amount')).order_by('billing__category')

    return render(request, 'billing/payment_analysis.html', {'analysis': analysis})

# Average Payment Amount
def average_payment(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        average_payment = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).aggregate(average=Sum('amount') / Count('id'))['average'] or 0
    else:
        average_payment = Payment.objects.aggregate(average=Sum('amount') / Count('id'))['average'] or 0

    return render(request, 'billing/average_payment.html', {'average_payment': average_payment})

# Largest Payment
def largest_payment(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        largest_payment = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).order_by('-amount').first()

        top_payments = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        ).order_by('-amount')[:10]
    else:
        largest_payment = Payment.objects.order_by('-amount').first()
        top_payments = Payment.objects.order_by('-amount')[:10]

    return render(request, 'billing/largest_payment.html', {
        'largest_payment': largest_payment,
        'top_payments': top_payments,
    })


def payments_by_method(request):
    user = request.user
    methods = []
    total_revenue = 0
    color_palette = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#6f42c1']

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        base_query = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        )
    else:
        base_query = Payment.objects.all()

    # Get payment methods with totals
    methods = list(
        base_query.values('method')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Add display names and colors
    method_choices = dict(Payment.METHOD_CHOICES)
    for idx, method in enumerate(methods):
        method['get_method_display'] = method_choices.get(method['method'], method['method'])
        method['color'] = color_palette[idx % len(color_palette)]

    # Calculate total revenue
    total_revenue = sum(m['total'] for m in methods) if methods else 0

    context = {
        'methods': methods,
        'total_revenue': total_revenue,
        'current_year': datetime.now().year
    }

    return render(request, 'billing/payments_by_method.html', context)




def get_user_billing_queryset(user):
    if user.is_superuser:
        return Billing.objects.all()
    try:
        assignment = user.assignment
        if assignment.mmda:
            return Billing.objects.filter(mmda=assignment.mmda)
        elif assignment.region:
            return Billing.objects.filter(region=assignment.region)
    except UserAssignment.DoesNotExist:
        return Billing.objects.none()


'''def accumulated_bill_report(request):
    user = request.user
    current_year = datetime.now().year
    report_data = []

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region or MMDA.")

        assigned_region = user_assignment.region
        assigned_mmda = user_assignment.mmda

        billings = Billing.objects.filter(
            account__region=assigned_region,
            account__mmda=assigned_mmda
        )
    else:
        billings = Billing.objects.all()

    total_due = 0  # ✅ Initialize total_due

    for year in range(current_year, current_year - 4, -1):
        yearly_billings = billings.filter(accounting_year=year)

        accumulated_amount = yearly_billings.aggregate(Sum('amount'))['amount__sum'] or 0
        paid_amount = yearly_billings.aggregate(Sum('total_paid'))['total_paid__sum'] or 0
        amount_due = accumulated_amount - paid_amount

        total_due += amount_due  # ✅ Update total_due for template

        if accumulated_amount > 0 or paid_amount > 0:  # Avoid empty years
            report_data.append({
                'year': year,
                'accumulated_amount': accumulated_amount,
                'paid_amount': paid_amount,
                'amount_due': amount_due,
                'action': f"/billing/report/{year}"
            })

    return render(request, 'billing/accumulated_owing.html', {
        'report_data': report_data,
        'total_due': total_due  # ✅ Now available in the template
    })'''


def accumulated_bill_report(request):
    user = request.user
    current_year = datetime.now().year
    report_data = []

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region or MMDA.")

        assigned_region = user_assignment.region
        assigned_mmda = user_assignment.mmda

        billings = Billing.objects.filter(
            account__region=assigned_region,
            account__mmda=assigned_mmda
        )
    else:
        billings = Billing.objects.all()

    total_due = 0
    total_owing = 0
    total_paid = 0

    for year in range(current_year, current_year - 4, -1):
        yearly_billings = billings.filter(accounting_year=year)

        accumulated_amount = yearly_billings.aggregate(Sum('amount'))['amount__sum'] or 0
        paid_amount = yearly_billings.aggregate(Sum('total_paid'))['total_paid__sum'] or 0
        amount_due = accumulated_amount - paid_amount

        total_due += amount_due
        total_owing += accumulated_amount
        total_paid += paid_amount

        if accumulated_amount > 0 or paid_amount > 0:
            report_data.append({
                'year': year,
                'accumulated_amount': accumulated_amount,
                'paid_amount': paid_amount,
                'amount_due': amount_due,
                'action': f"/billing/report/{year}"
            })

    return render(request, 'billing/accumulated_owing.html', {
        'report_data': report_data,
        'total_due': total_due,
        'total_owing': total_owing,
        'total_paid': total_paid,  # ✅ Add this
    })



def billing_report(request, account_id):
    try:
        # Fetch the billing records for the specified account
        billings = Billing.objects.filter(id=account_id).order_by('accounting_year')

        if not billings.exists():
            # Return an error message if no billing records are found
            return render(request, 'billing_report.html', {'error': 'No billing records found for this account.'})

        # Initialize report data and the previous closing balance
        report_data = []
        previous_closing_balance = Decimal(0)

        for billing in billings:
            # Get payments related to the current billing record
            payments = billing.payments.all()
            payment_details = []
            total_paid = Decimal(0)  # Initialize total paid for the year

            # Collect payment details for the year
            for payment in payments:
                payment_amount = Decimal(payment.amount)
                payment_details.append({
                    'date': payment.payment_date,
                    'payment_mode': payment.method,
                    'paid': payment_amount,
                })
                total_paid += payment_amount

            # Calculate brought forward balance (B/F)
            brought_forward = previous_closing_balance if previous_closing_balance > 0 else Decimal(0)

            # Safely calculate total due and other fields
            year_bill = Decimal(billing.amount or 0)  # Ensure amount is not None
            total_due = billing.amount + brought_forward 
            closing_balance = total_due - total_paid

            # Handle percentage calculations safely to avoid division by zero
            percentage_closing_balance_over_year_bill = ((closing_balance / year_bill) * 100) if year_bill > 0 else 0
            percentage_paid_over_closing_balance = ((total_paid / closing_balance) * 100) if closing_balance > 0 else 0
            percentage_paid_over_year_bill = ((total_paid / year_bill) * 100) if year_bill > 0 else 0

            # Append the data for the current year to the report
            report_data.append({
                'year': billing.accounting_year,
                'brought_forward': brought_forward,
                'year_bill': year_bill,
                'total_due': total_due,
                'total_paid': total_paid,
                'closing_balance': closing_balance,
                'percentage_closing_balance_over_year_bill': percentage_closing_balance_over_year_bill,
                'percentage_paid_over_closing_balance': percentage_paid_over_closing_balance,
                'percentage_paid_over_year_bill': percentage_paid_over_year_bill,
                'payment_details': payment_details,
            })

            # Update the carried-forward balance for the next year
            previous_closing_balance = closing_balance

        # Debugging output for validation
        print("Billings for account ID:", account_id, ":", list(billings))
        print("Generated Report Data:", report_data)

        # Prepare context for rendering the template
        context = {
            'report_data': report_data,
            'account': billings.first().account,  # Use the first billing's account details
        }
        return render(request, 'billing_report.html', context)

    except Exception as e:
        # Log the error and return a friendly error message
        print("Error occurred in billing_report:", str(e))
        return HttpResponse(f"An error occurred while generating the report: {e}", status=500)



def billing_logs(request):
    """
    View to display billing audit logs for the end user.
    """
    logs = BillingAudit.objects.all().order_by('-changed_at')  # Order by most recent logs
    context = {
        'logs': logs,
    }
    return render(request, 'billing/billing_logs.html', context)



def billing_logs(request):
    logs_list = BillingAudit.objects.all()
    paginator = Paginator(logs_list, 10)  # 10 logs per page
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    return render(request, 'billing/billing_logs.html', {'logs': logs})



def search_billings(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    bills = Billing.objects.filter(
        models.Q(ghana_card__icontains=query) |
        models.Q(id__icontains=query) |
        models.Q(recipient_name__icontains=query) |
        models.Q(contact_number__icontains=query)
    ).values('id', 'recipient_name', 'amount', 'payment_status')

    return JsonResponse(list(bills), safe=False)


def paynow(request):
    """Render the page for entering the Ghana Card number."""
    return render(request, 'paynow.html')



def enter_ghana_card(request):
    bill = None  # Ensure bill is always defined

    if request.method == 'POST':
        ghana_card = request.POST.get('ghana_card')
        bill = Billing.objects.filter(ghana_card=ghana_card).first()

    return render(request, 'paynow.html', {'bill': bill})



def fetch_bill(request):
    ghana_card = request.GET.get('ghana_card')
    
    if ghana_card:
        bill = Billing.objects.filter(ghana_card=ghana_card).first()
        if bill:
            return JsonResponse({
                'bill': bill.id,
                'first_name': bill.first_name,
                'surname': bill.surname,
                'gender': bill.gender,
                'date_of_birth': bill.date_of_birth
            })
        else:
            return JsonResponse({'error': 'No bill found for this Ghana Card.'})
    
    return JsonResponse({'error': 'Invalid request.'})



def fetch_ghana_card(request):
    ghana_card = request.GET.get('ghana_card', '').strip()
    
    if not ghana_card:
        return JsonResponse({"error": "Ghana Card number is required"}, status=400)

    # Mock database lookup
    user_data = {
        "GHA-1234567890-01": {
            "first_name": "JAMES",
            "surname": "GARDERNER",
            "gender": "Male",
            "date_of_birth": "2020-02-01",
            "bill_id": 123  # Example bill ID
        }
    }

    if ghana_card in user_data:
        return JsonResponse(user_data[ghana_card])
    else:
        return JsonResponse({"error": "No record found"}, status=404)


def print_bill(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)

    return render(request, 'billing/print_bill.html', {
        'bill': bill,
        'mmda': bill.mmda  # Directly use the ForeignKey reference
    })


# customer statement view
def customer_statement(request):
    statements = CustomerStatement.objects.all()  # You can filter based on user or other criteria
    return render(request, 'customer_stm.html', {'statements': statements})


def statement(request, bill_id):
    # 1. Get the billing record
    billing = get_object_or_404(Billing, id=bill_id)
    
    # 2. Get related payments/statements
    # Assuming you have a Payment model with ForeignKey to Billing
    payments = Payment.objects.filter(billing=billing).select_related(
        'dr_account', 
        'cr_account'
    )
    
    # 3. Prepare statements data
    statements = []
    for payment in payments:
        statements.append({
            'id': payment.id,
            'payment_id': payment.transaction_id,
            'customer_name': billing.recipient_name,
            'dr_account': {'id': payment.dr_account.account_number},
            'dr_account_name': payment.dr_account.name,
            'cr_account': {'id': payment.cr_account.account_number},
            'cr_account_name': payment.cr_account.name,
            'year_bill': billing.accounting_year,
            'date_generated': payment.payment_date,
            'amount': payment.amount,
            'method': payment.get_method_display()
        })
    
    # 4. Create context
    context = {
        'statements': statements,
        'billing': billing  # Pass the billing object if needed in template
    }
    
    return render(request, 'customer_stm.html', context)

    # Fetch related payments
    payments = billing.payments.all()  # Assuming related_name='payments'

    # Calculate total paid
    total_paid = sum((Decimal(payment.amount) for payment in payments), Decimal(0))

    # Safely calculate financials
    year_bill = Decimal(billing.amount or 0)
    closing_balance = year_bill - total_paid
    percentage_paid = (total_paid / year_bill) * 100 if year_bill > 0 else 0

    # Context for rendering the statement
    context = {
        'billing': billing,
        'payments': payments,
        'year_bill': year_bill,
        'total_paid': total_paid,
        'closing_balance': closing_balance,
        'percentage_paid': percentage_paid,
    }

    return render(request, 'billing/statement.html', context)


def graph_view(request):
    user = request.user
    base_query = Payment.objects.all()
    
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        
        base_query = base_query.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        )

    # Payment method distribution
    payment_counts = list(
        base_query.values('method')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Payment trends over time
    payment_trends = list(
        base_query.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # Convert Decimal values to float and format dates
    for trend in payment_trends:
        trend['total'] = float(trend['total']) if trend['total'] else 0.0
        trend['month'] = trend['month'].strftime("%B %Y")

    # Revenue target analysis
    revenue_data = []
    for target in RevenueTarget.objects.all():
        collected = base_query.filter(
            payment_date__year=target.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        revenue_data.append({
            'year': target.year,
            'target': float(target.target) if target.target else 0.0,
            'collected': float(collected),
            'percentage_achieved': (float(collected) / float(target.target) * 100) if target.target > 0 else 0,
        })

    # Summary metrics - Fixed missing closing parentheses
    total_revenue = float(base_query.aggregate(Sum('amount'))['amount__sum'] or 0.0)
    pending_amount = float(Billing.objects.filter(
        payment_status__in=['unpaid', 'partly_paid']
    ).aggregate(Sum('closing_balance'))['closing_balance__sum'] or 0.0)
    revenue_target = float(RevenueTarget.objects.aggregate(Sum('target'))['target__sum'] or 0.0)
    average_payment = float(base_query.aggregate(avg=Sum('amount') / Count('id'))['avg']) if base_query.exists() else 0.0

    context = {
        'payment_methods': json.dumps([pc['method'] for pc in payment_counts]),
        'payment_counts': json.dumps([pc['count'] for pc in payment_counts]),
        'payment_months': json.dumps([pt['month'] for pt in payment_trends]),
        'payment_totals': json.dumps([pt['total'] for pt in payment_trends]),
        'revenue_data': json.dumps(revenue_data),
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'revenue_target': revenue_target,
        'average_payment': average_payment,
    }

    return render(request, 'billing/graph_view.html', context)








'''def graph_view(request):
    user = request.user
    base_query = Payment.objects.all()

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        
        base_query = base_query.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        )

    # Payment trends over time
    payment_trends = list(
        base_query.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # Revenue trend for Chart.js
    revenue_trends = {
        'labels': [t['month'].strftime("%B %Y") for t in payment_trends],
        'data': [float(t['total']) for t in payment_trends],
    }

    # Payment method distribution (optional future use)
    payment_counts = list(
        base_query.values('method')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Revenue target analysis
    revenue_targets = RevenueTarget.objects.all()
    revenue_data = []
    for target in RevenueTarget.objects.all():
        collected = base_query.filter(
            payment_date__year=target.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_data.append({
            'year': target.year,
            'target': target.target,
            'collected': collected,
            'percentage_achieved': (collected / target.target * 100) if target.target > 0 else 0,
        })

    context = {
        'payment_methods': [entry['method'] for entry in payment_counts],
        'payment_counts': [entry['count'] for entry in payment_counts],
        'payment_months': [t['month'].strftime("%B %Y") for t in payment_trends],
        'payment_totals': [t['total'] for t in payment_trends],
        'revenue_data': revenue_data,
    }

    #return render(request, 'billing/graph.html', context)


    # Summary cards
    total_revenue = base_query.aggregate(Sum('amount'))['amount__sum'] or 0
    pending_amount = Billing.objects.filter(
    payment_status__in=['unpaid', 'partly_paid']
        ).aggregate(Sum('closing_balance'))['closing_balance__sum'] or 0  # Changed to closing_balance
    revenue_target = revenue_targets.aggregate(Sum('target'))['target__sum'] or 0
    average_payment = base_query.aggregate(avg=Sum('amount') / Count('id'))['avg'] if base_query.exists() else 0

    # Recent payments
    recent_payments = base_query.select_related('billing', 'billing__account').order_by('-payment_date')[:10]

    context = {
        'revenue_trends': revenue_trends,
        'payment_methods': [entry['method'] for entry in payment_counts],
        'payment_counts': [entry['count'] for entry in payment_counts],
        'revenue_data': revenue_data,
        'total_revenue': total_revenue,

        'revenue_target': revenue_target,
        'average_payment': average_payment,
        'payments': recent_payments,
    }

    return render(request, 'billing/graph.html', context)'''







def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['site'] = get_current_site(self.request)
    return context



def payment_detail(request, pk):
    try:
        payment = get_object_or_404(
            Payment.objects.select_related('billing'),
            pk=pk
        )
        context = {
            'payment': payment,
            'billing': payment.billing,
            'related_payments': Payment.objects.filter(billing=payment.billing)
                                               .exclude(pk=pk)
                                               .order_by('-payment_date')[:5]
        }
        return render(request, 'billing/payment_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error accessing payment {pk}: {str(e)}")
        raise Http404("Payment record could not be retrieved")


class TransactionListView(ListView):
    model = Payment
    template_name = 'billing/transaction_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return Payment.objects.select_related('billing').order_by('-payment_date')



def payment_analytics(request):
    stats = Payment.objects.aggregate(
        average_payment=Avg('amount'),
        total_payments=Count('id'),
        total_revenue=Sum('amount'),
        min_payment=Min('amount'),
        max_payment=Max('amount')
    )
    
    # Debugging: Print the stats to the console to ensure it's being populated correctly
    print(stats)

    return render(request, 'billing/payment_analytics.html', stats)


def export_outstanding(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
            
        base_query = Payment.objects.filter(
            billing__account__region=user_assignment.region,
            billing__account__mmda=user_assignment.mmda
        )
    else:
        base_query = Payment.objects.all()

    payments = base_query.annotate(
        year=ExtractYear('payment_date'),
        amount_due=ExpressionWrapper(
            Coalesce(F('billing__total_due'), 0) - Coalesce(F('amount'), 0),
            output_field=DecimalField()
        )
    ).filter(amount_due__gt=0)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="outstanding_payments.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Year', 
        'Accumulated Amount', 
        'Paid', 
        'Amount Due', 
        'Payment Method',
        'Payment Date'
    ])
    
    for payment in payments:
        writer.writerow([
            payment.year,
            payment.billing.total_due,
            payment.amount,
            payment.amount_due,
            payment.get_method_display(),
            payment.payment_date.strftime("%Y-%m-%d")
        ])
    
    return response


