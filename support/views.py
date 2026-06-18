"""
Views for Support app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    SupportTicket, TicketResponse, TechnicalManual, FAQ
)


# Support Tickets
@login_required
def support_ticket_list(request):
    """List support tickets."""
    if request.user.is_staff:
        tickets = SupportTicket.objects.all().order_by('-created_at')
    else:
        tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page')
    tickets_page = paginator.get_page(page)
    return render(request, 'support/support_ticket_list.html', {
        'tickets': tickets_page,
        'status_filter': status_filter,
    })


@login_required
def support_ticket_my_list(request):
    """My support tickets."""
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'support/support_ticket_my_list.html', {'tickets': tickets})


@login_required
def support_ticket_create(request):
    """Create support ticket."""
    if request.method == 'POST':
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=request.POST.get('subject', ''),
            description=request.POST.get('description', ''),
            priority=request.POST.get('priority', 'medium')
        )
        messages.success(request, "Support ticket created successfully.")
        return redirect('support:support-ticket-detail', ticket_id=ticket.id)
    
    return render(request, 'support/support_ticket_create.html')


def support_ticket_detail(request, ticket_id):
    """Support ticket detail."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    responses = TicketResponse.objects.filter(ticket=ticket)
    return render(request, 'support/support_ticket_detail.html', {'ticket': ticket, 'responses': responses})


@login_required
def support_ticket_update(request, ticket_id):
    """Update support ticket."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        ticket.subject = request.POST.get('subject', ticket.subject)
        ticket.description = request.POST.get('description', ticket.description)
        ticket.save()
        messages.success(request, "Ticket updated successfully.")
        return redirect('support:support-ticket-detail', ticket_id=ticket_id)
    
    return render(request, 'support/support_ticket_edit.html', {'ticket': ticket})


@login_required
def support_ticket_close(request, ticket_id):
    """Close support ticket."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        ticket.status = 'closed'
        ticket.save()
        messages.success(request, "Ticket closed.")
        return redirect('support:support-ticket-detail', ticket_id=ticket_id)
    
    return render(request, 'support/support_ticket_close.html', {'ticket': ticket})


@login_required
def support_ticket_reopen(request, ticket_id):
    """Reopen support ticket."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        ticket.status = 'open'
        ticket.save()
        messages.success(request, "Ticket reopened.")
        return redirect('support:support-ticket-detail', ticket_id=ticket_id)
    
    return redirect('support:support-ticket-detail', ticket_id=ticket_id)


@login_required
def support_ticket_assign(request, ticket_id):
    """Assign ticket (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            ticket.assigned_to = User.objects.get(id=assigned_to_id)
            ticket.save()
            messages.success(request, "Ticket assigned.")
    
    return redirect('support:support-ticket-detail', ticket_id=ticket_id)


# Ticket Responses
def ticket_response_list(request, ticket_id):
    """List ticket responses."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    responses = TicketResponse.objects.filter(ticket=ticket)
    return render(request, 'support/ticket_response_list.html', {'ticket': ticket, 'responses': responses})


@login_required
def ticket_response_create(request, ticket_id):
    """Create ticket response."""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        TicketResponse.objects.create(
            ticket=ticket,
            user=request.user,
            message=request.POST.get('message', '')
        )
        messages.success(request, "Response added.")
        return redirect('support:support-ticket-detail', ticket_id=ticket_id)
    
    return render(request, 'support/ticket_response_create.html', {'ticket': ticket})


def ticket_response_detail(request, response_id):
    """Ticket response detail."""
    response = get_object_or_404(TicketResponse, id=response_id)
    return render(request, 'support/ticket_response_detail.html', {'response': response})


@login_required
def ticket_response_update(request, response_id):
    """Update ticket response."""
    response = get_object_or_404(TicketResponse, id=response_id, user=request.user)
    
    if request.method == 'POST':
        response.message = request.POST.get('message', response.message)
        response.save()
        messages.success(request, "Response updated.")
        return redirect('support:support-ticket-detail', ticket_id=response.ticket.id)
    
    return render(request, 'support/ticket_response_edit.html', {'response': response})


@login_required
def ticket_response_delete(request, response_id):
    """Delete ticket response."""
    response = get_object_or_404(TicketResponse, id=response_id, user=request.user)
    
    if request.method == 'POST':
        ticket_id = response.ticket.id
        response.delete()
        messages.success(request, "Response deleted.")
        return redirect('support:support-ticket-detail', ticket_id=ticket_id)
    
    return render(request, 'support/ticket_response_delete.html', {'response': response})


# Ticket Filtering
def support_ticket_filter(request):
    """Filter support tickets."""
    status = request.GET.get('status')
    tickets = SupportTicket.objects.all()
    
    if status:
        tickets = tickets.filter(status=status)
    
    return render(request, 'support/support_ticket_filter.html', {'tickets': tickets})


def support_ticket_by_status(request, status):
    """Tickets by status."""
    tickets = SupportTicket.objects.filter(status=status)
    return render(request, 'support/support_ticket_by_status.html', {'tickets': tickets, 'status': status})


def support_ticket_by_priority(request, priority):
    """Tickets by priority."""
    tickets = SupportTicket.objects.filter(priority=priority)
    return render(request, 'support/support_ticket_by_priority.html', {'tickets': tickets, 'priority': priority})


def support_ticket_search(request):
    """Search support tickets."""
    query = request.GET.get('q', '')
    tickets = SupportTicket.objects.filter(Q(subject__icontains=query) | Q(description__icontains=query))
    return render(request, 'support/support_ticket_search.html', {'tickets': tickets, 'query': query})


# Technical Manuals
def technical_manual_list(request):
    """List technical manuals."""
    manuals = TechnicalManual.objects.filter(is_active=True)
    return render(request, 'support/technical_manual_list.html', {'manuals': manuals})


def technical_manual_detail(request, manual_id):
    """Technical manual detail."""
    manual = get_object_or_404(TechnicalManual, id=manual_id)
    return render(request, 'support/technical_manual_detail.html', {'manual': manual})


@login_required
def technical_manual_download(request, manual_id):
    """Download technical manual."""
    manual = get_object_or_404(TechnicalManual, id=manual_id)
    messages.info(request, "Manual download coming soon.")
    return redirect('support:technical-manual-detail', manual_id=manual_id)


@login_required
def technical_manual_create(request):
    """Create technical manual (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:technical-manual-list')
    
    if request.method == 'POST':
        TechnicalManual.objects.create(
            title=request.POST.get('title', ''),
            content=request.POST.get('content', '')
        )
        messages.success(request, "Manual created.")
        return redirect('support:technical-manual-list')
    
    return render(request, 'support/technical_manual_create.html')


@login_required
def technical_manual_update(request, manual_id):
    """Update technical manual (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:technical-manual-list')
    
    manual = get_object_or_404(TechnicalManual, id=manual_id)
    
    if request.method == 'POST':
        manual.title = request.POST.get('title', manual.title)
        manual.save()
        messages.success(request, "Manual updated.")
        return redirect('support:technical-manual-detail', manual_id=manual_id)
    
    return render(request, 'support/technical_manual_edit.html', {'manual': manual})


@login_required
def technical_manual_delete(request, manual_id):
    """Delete technical manual (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:technical-manual-list')
    
    manual = get_object_or_404(TechnicalManual, id=manual_id)
    
    if request.method == 'POST':
        manual.delete()
        messages.success(request, "Manual deleted.")
        return redirect('support:technical-manual-list')
    
    return render(request, 'support/technical_manual_delete.html', {'manual': manual})


def technical_manual_by_category(request, category_id):
    """Manuals by category."""
    manuals = TechnicalManual.objects.filter(category_id=category_id)
    return render(request, 'support/technical_manual_by_category.html', {'manuals': manuals})


# FAQs
def faq_list(request):
    """List FAQs."""
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'support/faq_list.html', {'faqs': faqs})


def faq_detail(request, faq_id):
    """FAQ detail."""
    faq = get_object_or_404(FAQ, id=faq_id)
    return render(request, 'support/faq_detail.html', {'faq': faq})


@login_required
def faq_create(request):
    """Create FAQ (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:faq-list')
    
    if request.method == 'POST':
        FAQ.objects.create(
            question=request.POST.get('question', ''),
            answer=request.POST.get('answer', '')
        )
        messages.success(request, "FAQ created.")
        return redirect('support:faq-list')
    
    return render(request, 'support/faq_create.html')


@login_required
def faq_update(request, faq_id):
    """Update FAQ (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:faq-list')
    
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.question = request.POST.get('question', faq.question)
        faq.answer = request.POST.get('answer', faq.answer)
        faq.save()
        messages.success(request, "FAQ updated.")
        return redirect('support:faq-detail', faq_id=faq_id)
    
    return render(request, 'support/faq_edit.html', {'faq': faq})


@login_required
def faq_delete(request, faq_id):
    """Delete FAQ (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('support:faq-list')
    
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.delete()
        messages.success(request, "FAQ deleted.")
        return redirect('support:faq-list')
    
    return render(request, 'support/faq_delete.html', {'faq': faq})


def faq_by_category(request, category_id):
    """FAQs by category."""
    faqs = FAQ.objects.filter(category_id=category_id)
    return render(request, 'support/faq_by_category.html', {'faqs': faqs})


def faq_search(request):
    """Search FAQs."""
    query = request.GET.get('q', '')
    faqs = FAQ.objects.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    return render(request, 'support/faq_search.html', {'faqs': faqs, 'query': query})


@login_required
def faq_helpful(request, faq_id):
    """Mark FAQ as helpful."""
    faq = get_object_or_404(FAQ, id=faq_id)
    faq.helpful_count = (faq.helpful_count or 0) + 1
    faq.save()
    messages.success(request, "Thank you for your feedback.")
    return redirect('support:faq-detail', faq_id=faq_id)


# Support Analytics
@login_required
def support_analytics(request):
    """Support analytics (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    total_tickets = SupportTicket.objects.count()
    return render(request, 'support/support_analytics.html', {'total_tickets': total_tickets})


@login_required
def support_ticket_analytics(request):
    """Ticket analytics (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'support/support_ticket_analytics.html')


@login_required
def support_response_time_analytics(request):
    """Response time analytics (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'support/support_response_time_analytics.html')
