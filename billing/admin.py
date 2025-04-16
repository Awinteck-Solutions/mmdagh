'''from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from .models import Billing, Rate, Payment, PaymentMethodVolume, RevenueTarget, AccumulatedOwing,BillingAudit



# Define BillingAuditInline
class BillingAuditInline(admin.TabularInline):
    model = BillingAudit
    extra = 0  # No empty extra rows
    readonly_fields = ('field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')  # Logs are read-only
    can_delete = False  # Prevent manual deletion of logs


# Billing Admin

class BillingAdmin(admin.ModelAdmin):
    list_display = (
        'account', 'brought_forward', 'amount', 'total_due',
        'total_paid', 'closing_balance', 'payment_status', 'created_at', 'rooms'
    )
    list_filter = ('payment_status',)
    search_fields = ('account__ghana_card', 'account__first_name', 'account__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('brought_forward', 'total_due', 'total_paid', 'closing_balance')
    actions = ['mark_as_paid']

    # Inline logs
    inlines = [BillingAuditInline]

def save_model(self, request, obj, form, change):
    """
    Logs changes or creation of Billing objects.
    """
    if not change:  # If this is a new Billing object
        BillingAudit.objects.create(
            billing=obj,
            field_name="__all__",
            old_value="None",
            new_value=str(obj),
            changed_by=request.user
        )
    else:  # If this is an update to an existing Billing object
        for field, old_value in form.initial.items():
            new_value = form.cleaned_data.get(field)
            if old_value != new_value:  # Log only if the field's value has changed
                BillingAudit.objects.create(
                    billing=obj,
                    field_name=field,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=request.user
                )
    super().save_model(request, obj, form, change)



def mark_as_paid(self, request, queryset):
    """
    Log changes when marking bills as paid.
    """
    for billing in queryset:
        BillingAudit.objects.create(
            billing=billing,
            field_name="payment_status",
            old_value=billing.payment_status,
            new_value="paid",
            changed_by=request.user
        )
        BillingAudit.objects.create(
            billing=billing,
            field_name="closing_balance",
            old_value=billing.closing_balance,
            new_value=0,
            changed_by=request.user
        )
    updated_count = queryset.update(payment_status='paid', closing_balance=0)
    self.message_user(request, f"{updated_count} bill(s) marked as paid.")

def delete_model(self, request, obj):
    """
    Logs deletion of a Billing object.
    """
    BillingAudit.objects.create(
        billing=obj,
        field_name="__all__",
        old_value=str(obj),
        new_value="Deleted",
        changed_by=request.user
    )
    super().delete_model(request, obj)

def delete_queryset(self, request, queryset):
    """
    Logs bulk deletions of Billing objects.
    """
    for obj in queryset:
        BillingAudit.objects.create(
            billing=obj,
            field_name="__all__",
            old_value=str(obj),
            new_value="Deleted",
            changed_by=request.user
        )
    queryset.delete()


admin.site.register(Billing, BillingAdmin)




# Payment Admin
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'amount', 'payment_date', 'method')
    list_filter = ('payment_date', 'method')
    search_fields = ('billing__account__ghana_card', 'billing__account__first_name', 'billing__account__last_name')
    ordering = ('-payment_date',)

    actions = [
        'revenue_overview',
        'popular_payment_method',
        'average_payment_amount',
        'payment_trends_over_time',
    ]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'amount', 'payment_date', 'method')
    list_filter = ('payment_date', 'method')
    search_fields = ('billing__account__ghana_card', 'billing__account__first_name', 'billing__account__last_name')
    ordering = ('-payment_date',)

    def save_model(self, request, obj, form, change):
        """
        Logs changes or creation of Payment objects.
        """
        if not change:  # New Payment object
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value="None",
                new_value=f"Payment of GHS {obj.amount} added.",
                changed_by=request.user
            )
        else:  # Updated Payment object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=obj.billing,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Payment object.
        """
        BillingAudit.objects.create(
            billing=obj.billing,
            field_name="payment",
            old_value=f"Payment of GHS {obj.amount}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Payment objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value=f"Payment of GHS {obj.amount}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

    actions = [
        'revenue_overview',
        'popular_payment_method',
        'average_payment_amount',
        'payment_trends_over_time',
    ]

admin.site.register(Payment, PaymentAdmin)


    @admin.action(description="View Revenue Overview")
    def revenue_overview(self, request, queryset):
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        self.message_user(request, f"Total Revenue Collected: GHS {total_revenue:.2f}")

    @admin.action(description="View Most Popular Payment Method")
    def popular_payment_method(self, request, queryset):
        popular_method = Payment.objects.values('method').annotate(total=Count('id')).order_by('-total').first()
        if popular_method:
            method_name = popular_method['method']
            count = popular_method['total']
            self.message_user(request, f"Most Popular Payment Method: {method_name} with {count} transactions.")
        else:
            self.message_user(request, "No payment methods found.")

    @admin.action(description="View Average Payment Amount")
    def average_payment_amount(self, request, queryset):
        avg_amount = Payment.objects.aggregate(avg=Avg('amount'))['avg'] or 0
        self.message_user(request, f"Average Payment Amount: GHS {avg_amount:.2f}")

    @admin.action(description="View Payment Trends Over Time")
    def payment_trends_over_time(self, request, queryset):
        trends = Payment.objects.annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
        if trends:
            trend_message = ", ".join([f"{trend['month'].strftime('%B %Y')}: GHS {trend['total']:.2f}" for trend in trends])
            self.message_user(request, f"Payment Trends: {trend_message}")
        else:
            self.message_user(request, "No payment trends found.")

admin.site.register(Payment, PaymentAdmin)


# Payment Volume by Method Admin
class PaymentMethodVolumeAdmin(admin.ModelAdmin):
    list_display = ('method', 'volume')

admin.site.register(PaymentMethodVolume, PaymentMethodVolumeAdmin)


# Revenue Target Admin
class RevenueTargetAdmin(admin.ModelAdmin):
    list_display = ('year', 'target', 'total_collected', 'percentage_achieved')

    def total_collected(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        return f"GHS {total:.2f}"

    def percentage_achieved(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        if obj.target > 0:
            return f"{(total / obj.target) * 100:.2f}%"
        return "0.00%"

    total_collected.short_description = "Total Collected"
    percentage_achieved.short_description = "Percentage Achieved"

admin.site.register(RevenueTarget, RevenueTargetAdmin)


# Rate Admin
class RateAdmin(admin.ModelAdmin):
    list_display = ('category', 'rate')
    search_fields = ('category',)
    list_filter = ('category',)
    ordering = ('category',)

    def save_model(self, request, obj, form, change):
        """
        Logs creation or update of Rate objects.
        """
        if not change:  # New Rate object
            BillingAudit.objects.create(
                billing=None,  # No specific billing associated
                field_name="rate",
                old_value="None",
                new_value=f"Rate for {obj.category} set to {obj.rate}",
                changed_by=request.user
            )
        else:  # Update to an existing Rate object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=None,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Rate object.
        """
        BillingAudit.objects.create(
            billing=None,
            field_name="rate",
            old_value=f"Rate for {obj.category} at {obj.rate}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Rate objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=None,
                field_name="rate",
                old_value=f"Rate for {obj.category} at {obj.rate}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

admin.site.register(Rate, RateAdmin)


# Accumulated Owing Admin
@admin.register(AccumulatedOwing)
class AccumulatedOwingAdmin(admin.ModelAdmin):
    list_display = ('account', 'year', 'amount', 'created_at')
    list_filter = ('year',)
    search_fields = ('account__first_name', 'account__surname', 'account__ghana_card')
    ordering = ('-year', 'account')



@admin.register(BillingAudit)
class BillingAuditAdmin(admin.ModelAdmin):
    list_display = ('billing', 'field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')
    search_fields = ('field_name', 'billing__id', 'changed_by__username')
    list_filter = ('changed_at', 'field_name')'''



'''from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from .models import Billing, Rate, Payment, PaymentMethodVolume, RevenueTarget, AccumulatedOwing, BillingAudit

# Define BillingAuditInline
class BillingAuditInline(admin.TabularInline):
    model = BillingAudit
    extra = 0  # No empty extra rows
    readonly_fields = ('field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')  # Logs are read-only
    can_delete = False  # Prevent manual deletion of logs
    ordering = ('-changed_at',)  # Sort logs by most recent


# Billing Admin
class BillingAdmin(admin.ModelAdmin):
    list_display = (
        'account', 'brought_forward', 'amount', 'total_due',
        'total_paid', 'closing_balance', 'payment_status', 'created_at', 'rooms'
    )
    list_filter = ('payment_status',)
    search_fields = ('account__ghana_card', 'account__first_name', 'account__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('brought_forward', 'total_due', 'total_paid', 'closing_balance')
    actions = ['mark_as_paid']

    # Inline logs
    inlines = [BillingAuditInline]

    def save_model(self, request, obj, form, change):
        """
        Logs changes or creation of Billing objects.
        """
        if not change:  # If this is a new Billing object
            BillingAudit.objects.create(
                billing=obj,
                field_name="__all__",
                old_value="None",
                new_value=str(obj),
                changed_by=request.user
            )
        else:  # If this is an update to an existing Billing object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:  # Log only if the field's value has changed
                    BillingAudit.objects.create(
                        billing=obj,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def mark_as_paid(self, request, queryset):
        """
        Log changes when marking bills as paid.
        """
        for billing in queryset:
            BillingAudit.objects.create(
                billing=billing,
                field_name="payment_status",
                old_value=billing.payment_status,
                new_value="paid",
                changed_by=request.user
            )
            BillingAudit.objects.create(
                billing=billing,
                field_name="closing_balance",
                old_value=billing.closing_balance,
                new_value=0,
                changed_by=request.user
            )
        updated_count = queryset.update(payment_status='paid', closing_balance=0)
        self.message_user(request, f"{updated_count} bill(s) marked as paid.")

    def delete_model(self, request, obj):
        """
        Logs deletion of a Billing object.
        """
        BillingAudit.objects.create(
            billing=obj,
            field_name="__all__",
            old_value=str(obj),
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletions of Billing objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=obj,
                field_name="__all__",
                old_value=str(obj),
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

admin.site.register(Billing, BillingAdmin)


# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'amount', 'payment_date', 'method')
    list_filter = ('payment_date', 'method')
    search_fields = ('billing__account__ghana_card', 'billing__account__first_name', 'billing__account__last_name')
    ordering = ('-payment_date',)

    def save_model(self, request, obj, form, change):
        """
        Logs changes or creation of Payment objects.
        """
        if not change:  # New Payment object
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value="None",
                new_value=f"Payment of GHS {obj.amount} added.",
                changed_by=request.user
            )
        else:  # Updated Payment object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=obj.billing,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Payment object.
        """
        BillingAudit.objects.create(
            billing=obj.billing,
            field_name="payment",
            old_value=f"Payment of GHS {obj.amount}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Payment objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value=f"Payment of GHS {obj.amount}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

    @admin.action(description="View Revenue Overview")
    def revenue_overview(self, request, queryset):
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        self.message_user(request, f"Total Revenue Collected: GHS {total_revenue:.2f}")

    @admin.action(description="View Most Popular Payment Method")
    def popular_payment_method(self, request, queryset):
        popular_method = Payment.objects.values('method').annotate(total=Count('id')).order_by('-total').first()
        if popular_method:
            method_name = popular_method['method']
            count = popular_method['total']
            self.message_user(request, f"Most Popular Payment Method: {method_name} with {count} transactions.")
        else:
            self.message_user(request, "No payment methods found.")

    @admin.action(description="View Average Payment Amount")
    def average_payment_amount(self, request, queryset):
        avg_amount = Payment.objects.aggregate(avg=Avg('amount'))['avg'] or 0
        self.message_user(request, f"Average Payment Amount: GHS {avg_amount:.2f}")

    @admin.action(description="View Payment Trends Over Time")
    def payment_trends_over_time(self, request, queryset):
        trends = Payment.objects.annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
        if trends:
            trend_message = ", ".join([f"{trend['month'].strftime('%B %Y')}: GHS {trend['total']:.2f}" for trend in trends])
            self.message_user(request, f"Payment Trends: {trend_message}")
        else:
            self.message_user(request, "No payment trends found.")

# Payment Volume by Method Admin
@admin.register(PaymentMethodVolume)
class PaymentMethodVolumeAdmin(admin.ModelAdmin):
    list_display = ('method', 'volume')


# Revenue Target Admin
@admin.register(RevenueTarget)
class RevenueTargetAdmin(admin.ModelAdmin):
    list_display = ('year', 'target', 'total_collected', 'percentage_achieved')

    def total_collected(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        return f"GHS {total:.2f}"

    def percentage_achieved(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        if obj.target > 0:
            return f"{(total / obj.target) * 100:.2f}%"
        return "0.00%"

    total_collected.short_description = "Total Collected"
    percentage_achieved.short_description = "Percentage Achieved"


# Rate Admin
@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('category', 'rate')
    search_fields = ('category',)
    list_filter = ('category',)
    ordering = ('category',)

    def save_model(self, request, obj, form, change):
        """
        Logs creation or update of Rate objects.
        """
        if not change:  # New Rate object
            BillingAudit.objects.create(
                billing=None,  # No specific billing associated
                field_name="rate",
                old_value="None",
                new_value=f"Rate for {obj.category} set to {obj.rate}",
                changed_by=request.user
            )
        else:  # Update to an existing Rate object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=None,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Rate object.
        """
        BillingAudit.objects.create(
            billing=None,
            field_name="rate",
            old_value=f"Rate for {obj.category} at {obj.rate}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Rate objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=None,
                field_name="rate",
                old_value=f"Rate for {obj.category} at {obj.rate}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()


# Accumulated Owing Admin
@admin.register(AccumulatedOwing)
class AccumulatedOwingAdmin(admin.ModelAdmin):
    list_display = ('account', 'year', 'amount', 'created_at')
    list_filter = ('year',)
    search_fields = ('account__first_name', 'account__surname', 'account__ghana_card')
    ordering = ('-year', 'account')


# Billing Audit Admin
@admin.register(BillingAudit)
class BillingAuditAdmin(admin.ModelAdmin):
    list_display = ('billing', 'field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')
    search_fields = ('field_name', 'billing__id', 'changed_by__username')
    list_filter = ('changed_at', 'field_name')'''





from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from .models import Billing, Rate, Payment, PaymentMethodVolume, RevenueTarget, AccumulatedOwing, BillingAudit
import logging


# Set up logging

logger = logging.getLogger(__name__)


# Define BillingAuditInline
class BillingAuditInline(admin.TabularInline):
    model = BillingAudit
    extra = 0  # No empty extra rows
    readonly_fields = ('field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')  # Logs are read-only
    can_delete = False  # Prevent manual deletion of logs
    ordering = ('-changed_at',)  # Sort logs by most recent

# Billing Admin
class BillingAdmin(admin.ModelAdmin):
    list_display = (
        'account', 'brought_forward', 'amount', 'total_due',
        'total_paid', 'closing_balance', 'payment_status', 'created_at', 'rooms'
    )
    list_filter = ('payment_status',)
    search_fields = ('account__ghana_card', 'account__first_name', 'account__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('brought_forward', 'total_due', 'total_paid', 'closing_balance')
    actions = ['mark_as_paid']

    # Inline logs
    inlines = [BillingAuditInline]

    def save_model(self, request, obj, form, change):
        """
        Logs changes or creation of Billing objects.
        """
        super().save_model(request, obj, form, change)
        
        # Create an audit log entry
        if not change:  # If this is a new Billing object
            BillingAudit.objects.create(
                billing=obj,
                field_name="__all__",
                old_value="None",
                new_value=str(obj),
                changed_by=request.user
            )
        else:  # If this is an update to an existing Billing object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:  # Log only if the field's value has changed
                    BillingAudit.objects.create(
                        billing=obj,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )

    def mark_as_paid(self, request, queryset):
        """
        Log changes when marking bills as paid.
        """
        for billing in queryset:
            BillingAudit.objects.create(
                billing=billing,
                field_name="payment_status",
                old_value=billing.payment_status,
                new_value="paid",
                changed_by=request.user
            )
            BillingAudit.objects.create(
                billing=billing,
                field_name="closing_balance",
                old_value=billing.closing_balance,
                new_value=0,
                changed_by=request.user
            )
        updated_count = queryset.update(payment_status='paid', closing_balance=0)
        self.message_user(request, f"{updated_count} bill(s) marked as paid.")

    def delete_model(self, request, obj):
        """
        Logs deletion of a Billing object.
        """
        BillingAudit.objects.create(
            billing=obj,
            field_name="__all__",
            old_value=str(obj),
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletions of Billing objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=obj,
                field_name="__all__",
                old_value=str(obj),
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

admin.site.register(Billing, BillingAdmin)

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'amount', 'payment_date', 'method')
    list_filter = ('payment_date', 'method')
    search_fields = ('billing__account__ghana_card', 'billing__account__first_name', 'billing__account__last_name')
    ordering = ('-payment_date',)

    def save_model(self, request, obj, form, change):
        """
        Logs changes or creation of Payment objects.
        """
        super().save_model(request, obj, form, change)
        
        # Create an audit log entry
        if not change:  # New Payment object
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value="None",
                new_value=f"Payment of GHS {obj.amount} added.",
                changed_by=request.user
            )
        else:  # Updated Payment object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=obj.billing,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Payment object.
        """
        BillingAudit.objects.create(
            billing=obj.billing,
            field_name="payment",
            old_value=f"Payment of GHS {obj.amount}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Payment objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=obj.billing,
                field_name="payment",
                old_value=f"Payment of GHS {obj.amount}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()

    @admin.action(description="View Revenue Overview")
    def revenue_overview(self, request, queryset):
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        self.message_user(request, f"Total Revenue Collected: GHS {total_revenue:.2f}")

    @admin.action(description="View Most Popular Payment Method")
    def popular_payment_method(self, request, queryset):
        popular_method = Payment.objects.values('method').annotate(total=Count('id')).order_by('-total').first()
        if popular_method:
            method_name = popular_method['method']
            count = popular_method['total']
            self.message_user(request, f"Most Popular Payment Method: {method_name} with {count} transactions.")
        else:
            self.message_user(request, "No payment methods found.")

    @admin.action(description="View Average Payment Amount")
    def average_payment_amount(self, request, queryset):
        avg_amount = Payment.objects.aggregate(avg=Avg('amount'))['avg'] or 0
        self.message_user(request, f"Average Payment Amount: GHS {avg_amount:.2f}")

    @admin.action(description="View Payment Trends Over Time")
    def payment_trends_over_time(self, request, queryset):
        trends = Payment.objects.annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
        if trends:
            trend_message = ", ".join([f"{trend['month'].strftime('%B %Y')}: GHS {trend['total']:.2f}" for trend in trends])
            self.message_user(request, f"Payment Trends: {trend_message}")
        else:
            self.message_user(request, "No payment trends found.")

# Payment Volume by Method Admin
@admin.register(PaymentMethodVolume)
class PaymentMethodVolumeAdmin(admin.ModelAdmin):
    list_display = ('method', 'volume')

# Revenue Target Admin
@admin.register(RevenueTarget)
class RevenueTargetAdmin(admin.ModelAdmin):
    list_display = ('year', 'target', 'total_collected', 'percentage_achieved')

    def total_collected(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        return f"GHS {total:.2f}"

    def percentage_achieved(self, obj):
        total = Payment.objects.filter(payment_date__year=obj.year).aggregate(total=Sum('amount'))['total'] or 0
        if obj.target > 0:
            return f"{(total / obj.target) * 100:.2f}%"
        return "0.00%"

    total_collected.short_description = "Total Collected"
    percentage_achieved.short_description = "Percentage Achieved"

# Rate Admin
'''@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('category', 'rate')
    search_fields = ('category',)
    list_filter = ('category',)
    ordering = ('category',)

    def save_model(self, request, obj, form, change):
        """
        Logs creation or update of Rate objects.
        """
        if not change:  # New Rate object
            BillingAudit.objects.create(
                billing=None,  # No specific billing associated
                field_name="rate",
                old_value="None",
                new_value=f"Rate for {obj.category} set to {obj.rate}",
                changed_by=request.user
            )
        else:  # Update to an existing Rate object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    BillingAudit.objects.create(
                        billing=None,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=request.user
                    )
        super().save_model(request, obj, form, change)


    def delete_model(self, request, obj):
        """
        Logs deletion of a Rate object.
        """
        BillingAudit.objects.create(
            billing=None,
            field_name="rate",
            old_value=f"Rate for {obj.category} at {obj.rate}",
            new_value="Deleted",
            changed_by=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Rate objects.
        """
        for obj in queryset:
            BillingAudit.objects.create(
                billing=None,
                field_name="rate",
                old_value=f"Rate for {obj.category} at {obj.rate}",
                new_value="Deleted",
                changed_by=request.user
            )
        queryset.delete()'''

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('category', 'rate')
    search_fields = ('category',)
    list_filter = ('category',)
    ordering = ('category',)

    def save_model(self, request, obj, form, change):
        """
        Logs creation or update of Rate objects.
        """
        if not change:  # New Rate object
            # Log the creation of a new rate without a billing reference
            logger.info(f"New rate created: {obj.category} - {obj.rate}")
        else:  # Update to an existing Rate object
            for field, old_value in form.initial.items():
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    # Log the change without a billing reference
                    logger.info(f"Rate updated: {field} changed from {old_value} to {new_value}")

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Logs deletion of a Rate object.
        """
        logger.info(f"Rate deleted: {obj.category} - {obj.rate}")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Logs bulk deletion of Rate objects.
        """
        for obj in queryset:
            logger.info(f"Rate deleted: {obj.category} - {obj.rate}")
        queryset.delete()

# Accumulated Owing Admin
@admin.register(AccumulatedOwing)
class AccumulatedOwingAdmin(admin.ModelAdmin):
    list_display = ('account', 'year', 'amount', 'created_at')
    list_filter = ('year',)
    search_fields = ('account__first_name', 'account__surname', 'account__ghana_card')
    ordering = ('-year', 'account')

# Billing Audit Admin
@admin.register(BillingAudit)
class BillingAuditAdmin(admin.ModelAdmin):
    list_display = ('billing', 'field_name', 'old_value', 'new_value', 'changed_at', 'changed_by')
    search_fields = ('field_name', 'billing__id', 'changed_by__username')
    list_filter = ('changed_at', 'field_name')

'''# Ensure that the admin site is registered with all the models
admin.site.register(Billing, BillingAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(RevenueTarget, RevenueTargetAdmin)
admin.site.register(PaymentMethodVolume, PaymentMethodVolumeAdmin)
admin.site.register(AccumulatedOwing, AccumulatedOwingAdmin)
admin.site.register(BillingAudit, BillingAuditAdmin)'''