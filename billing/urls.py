from django.urls import path
from . import views
from .views import revenue_target
#from .views import prepayment_report, owings_report
from .views import bill_list, export_bills_pdf, export_bills_excel,search_billings,print_bill,customer_statement,statement

urlpatterns = [
    path('generate_bill/<int:account_id>/', views.generate_bill, name='generate_bill'),
    path('bill_list/', views.bill_list, name='bill_list'),
    path('bill_detail/<int:bill_id>/', views.bill_detail, name='bill_detail'),  # Correct path


    path('payment/<int:bill_id>/', views.payment_form, name='payment_form'),
    path('revenue-account/', views.revenue_account, name='revenue_account'),
    path('unpaid_bills/', views.unpaid_bills, name='unpaid_bills'),
    path('billing/logs/', views.billing_logs, name='billing_logs'),
    path('payments/<int:pk>/', views.payment_detail, name='payment-detail'), 
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),


    path('revenue_summary/', views.revenue_summary, name='revenue_summary'),
    path('revenue-report/', views.total_revenue, name='monthly_revenue_report'),
    path('payment_trends/', views.payment_trends, name='payment_trends'),
    path('unpaid_bills/', views.unpaid_bills, name='unpaid_bills'),
    path('payment_analysis/', views.payment_analysis_by_category, name='payment_analysis'),
    path('average_payment/', views.average_payment, name='average_payment'),
    path('largest_payment/', views.largest_payment, name='largest_payment'),
    path('payments_by_method/', views.payments_by_method, name='payments_by_method'),
    path('revenue-target/',views.revenue_target, name='revenue_target'),
    path('graph/', views.graph_view, name='graph_view'),
    path('payment-analytics/', views.payment_analytics, name='payment_analytics'),
    path('export-outstanding/', views.export_outstanding, name='export-outstanding'),

    path('graph/payments-by-method/', views.payments_by_method, name='graph_payments_by_method'),
    path('graph/payment-trends/', views.payment_trends, name='graph_payment_trends'),
    path('graph/revenue-target/', views.revenue_target, name='revenue_target'),

    path('accumulated_owing/', views.accumulated_bill_report, name='accumulated_owing'),
    path('billing/report/<int:account_id>/', views.billing_report, name='billing_report'),
    #path('accumulated_report/', views.accumulated_report, name='accumulated_report'),
    #path('billing/report/positive/<int:account_id>/', owings_report, name='owings_report'),
    #path('billing/report/negative/<int:account_id>/', prepayment_report, name='prepayment_report'),

    #path('pay_now/', views.payment_form, name='pay_now'),
    path('search_billings/', search_billings, name='search_billings'),
    path('export_bills_pdf/', export_bills_pdf, name='export_bills_pdf'),
    path('export_bills_excel/', export_bills_excel, name='export_bills_excel'),
    path('paynow/', views.enter_ghana_card, name='paynow'),
    #path('paynow/', views.paynow, name='paynow'),

    path('paynow/', views.paynow, name='paynow'),
    path('fetch-bill/', views.fetch_bill, name='fetch_bill'),  # New AJAX endpoin
    path('fetch-ghana-card/', views.fetch_ghana_card, name='fetch_ghana_card'),  # Ensure this exists




    path('billing/export_unpaid_bills_pdf/', views.export_unpaid_bills_pdf, name='export_unpaid_bills_pdf'),
    path('billing/export_unpaid_bills_excel/', views.export_unpaid_bills_excel, name='export_unpaid_bills_excel'),
    path('billing/print_bill/<int:bill_id>/', views.print_bill, name='print_bill'),


    path('customer-statement/', views.customer_statement, name='customer_statement'),
    path('statement/<int:bill_id>/', views.statement, name='statement')

]


