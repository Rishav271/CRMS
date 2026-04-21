from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse

from .models import Event, Registration, Notification
import qrcode

# ---------------- HOME ----------------
def home(request):
    return render(request, 'events/home.html')


# ---------------- EVENT LIST ----------------
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


# ---------------- REGISTER USER ----------------
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'events/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'events/register.html', {'error': 'Username exists'})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')

    return render(request, 'events/register.html')


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    user = request.user

    my_events = Registration.objects.filter(user=user)
    all_events = Event.objects.all()
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]

    joined_event_ids = my_events.values_list('event_id', flat=True)

    return render(request, 'events/dashboard.html', {
        'my_events': my_events,
        'all_events': all_events,
        'joined_event_ids': joined_event_ids,
        'notifications': notifications
    })


# ---------------- REGISTER EVENT ----------------
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.is_paid:
        return redirect('payment', event_id=event.id)

    if not Registration.objects.filter(user=request.user, event=event).exists():
        Registration.objects.create(user=request.user, event=event)

        Notification.objects.create(
            user=request.user,
            message=f"You joined {event.title} 🎉"
        )

        messages.success(request, f"Joined {event.title}")
    else:
        messages.info(request, "Already joined")

    return redirect('dashboard')


# ---------------- PAYMENT ----------------
@login_required
def payment_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/payment.html', {'event': event})


@login_required
def payment_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    Registration.objects.get_or_create(user=request.user, event=event)

    Notification.objects.create(
        user=request.user,
        message=f"Payment done & joined {event.title} 💳"
    )

    messages.success(request, "Payment successful!")

    return redirect('dashboard')


# ---------------- UNREGISTER ----------------
@login_required
def unregister_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    Registration.objects.filter(user=request.user, event=event).delete()

    Notification.objects.create(
        user=request.user,
        message=f"You left {event.title} ❌"
    )

    messages.warning(request, "Event left")

    return redirect('dashboard')


# ---------------- LOGOUT ----------------
def custom_logout(request):
    logout(request)
    return redirect('login')


# ---------------- TICKET ----------------
@login_required
def ticket_view(request, event_id):
    registration = get_object_or_404(
        Registration,
        user=request.user,
        event_id=event_id
    )

    return render(request, "events/ticket.html", {
        "registration": registration
    })


# ---------------- QR ----------------
@login_required
def generate_qr(request, event_id):
    registration = get_object_or_404(
        Registration,
        user=request.user,
        event_id=event_id
    )

    data = f"User: {request.user.username} | Event: {registration.event.title}"

    qr = qrcode.make(data)

    response = HttpResponse(content_type="image/png")
    qr.save(response, "PNG")

    return response

from .models import Transaction
import uuid

@login_required
def payment_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # ✅ Create Registration
    registration, created = Registration.objects.get_or_create(
        user=request.user,
        event=event
    )

    # ✅ Save Transaction
    Transaction.objects.create(
        user=request.user,
        event=event,
        transaction_id=str(uuid.uuid4())[:10],  # random ID
        amount=event.price,
        payment_method="Card",
        status="SUCCESS"
    )

    messages.success(request, "✅ Payment Successful! 🎉")

    return redirect('dashboard')