from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket
from .forms import TicketForm
from django.contrib.admin.views.decorators import staff_member_required

def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'helpdesk/ticket_list.html', {'tickets': tickets})

def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'helpdesk/create_ticket.html', {'form': form})



'''#@staff_member_required
def manage_tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'helpdesk/manage_tickets.html', {'tickets': tickets})'''


from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Ticket

@staff_member_required
def manage_tickets(request):
    # Get filter parameters from request
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    # Base queryset
    tickets = Ticket.objects.select_related('user').order_by('-created_at')

    # Apply filters
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        tickets = tickets.filter(status=status_filter)

    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(tickets, 25)  # Show 25 tickets per page

    try:
        tickets_page = paginator.page(page)
    except PageNotAnInteger:
        tickets_page = paginator.page(1)
    except EmptyPage:
        tickets_page = paginator.page(paginator.num_pages)

    context = {
        'tickets': tickets_page,
        'page_obj': tickets_page,  # For pagination template
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search_query,
    }

    return render(request, 'helpdesk/manage_tickets.html', context)


from django.shortcuts import get_object_or_404

@staff_member_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, 'helpdesk/ticket_detail.html', {'ticket': ticket})


from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

@staff_member_required
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, f'Ticket #{pk} deleted successfully')
        return redirect('manage_tickets')
    
    # Optional: Handle GET requests differently if needed
    return redirect('ticket_detail', pk=pk)


#@staff_member_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('manage_tickets')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'helpdesk/update_ticket.html', {'form': form, 'ticket': ticket})
