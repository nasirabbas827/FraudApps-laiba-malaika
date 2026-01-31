from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import socket

from .models import (
    CustomerUser,
    Application,
    Review,
    AdminReviewLog,
    Feedback
)
from .forms import (
    RegisterForm,
    LoginForm,
    EditProfileForm,
    FeedbackForm
)
from .sentiment import analyze_sentiment_sentiwordnet


# ────────────────────────────────────────────────
#                   PUBLIC PAGES
# ────────────────────────────────────────────────

def index(request):
    """
    Landing page / home page of the application.
    No authentication required.
    """
    return render(request, 'index.html')


# ────────────────────────────────────────────────
#                 AUTHENTICATION
# ────────────────────────────────────────────────

def register_view(request):
    """
    User registration view.
    Creates a new CustomerUser account using RegisterForm.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    Custom login view (session-based, not using Django's auth backend).
    Checks username + password manually and sets session variables.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = CustomerUser.objects.get(username=username)

                if user.status != 'active':
                    messages.error(request, "Your account is not active. Please contact support.")
                    return render(request, 'login.html', {'form': form})

                if check_password(password, user.password):
                    # Set session data (very basic session auth)
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username

                    messages.success(request, f"Welcome {user.username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid password")

            except CustomerUser.DoesNotExist:
                messages.error(request, "User not found")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """
    Clears the entire session and logs the user out.
    """
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('index')


# ────────────────────────────────────────────────
#                   USER DASHBOARD
# ────────────────────────────────────────────────

def dashboard_view(request):
    """
    Main dashboard – shows user info and ranked list of applications
    (sorted by average sentiment score descending).
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, user_id=request.session['user_id'])

    # Most positively reviewed apps first
    applications = Application.objects.all().order_by('-avg_sentiment_score')

    return render(request, 'dashboard.html', {
        'user': user,
        'applications': applications
    })


def app_details(request, app_id):
    """
    Shows detailed view of one application + all its reviews.
    """
    app = get_object_or_404(Application, id=app_id)
    reviews = Review.objects.filter(app=app)

    return render(request, 'app_details.html', {
        'app': app,
        'reviews': reviews
    })


# ────────────────────────────────────────────────
#                    REVIEWS
# ────────────────────────────────────────────────

def add_review(request, app_id):
    """
    Allows logged-in users to submit a review + rating for an application.
    Features:
      • Basic duplicate/fake review detection (≥3 reviews = suspicious)
      • Sentiment analysis using SentiWordNet
      • Logs suspicious reviews to AdminReviewLog
    """
    if 'user_id' not in request.session:
        messages.error(request, "Login required.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, user_id=request.session['user_id'])
    app = get_object_or_404(Application, id=app_id)

    # Get client IP (note: this method is not reliable behind proxies/load balancers)
    ip_address = socket.gethostbyname(socket.gethostname())

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        try:
            rating = int(request.POST.get('rating'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid rating value.")
            return redirect('app_details', app_id=app.id)

        if not comment:
            messages.error(request, "Comment cannot be empty.")
            return redirect('app_details', app_id=app.id)

        # ── Sentiment Analysis ────────────────────────────────
        sentiment_label, sentiment_score = analyze_sentiment_sentiwordnet(comment)

        # Very naive fake review detection
        review_count_by_user_for_app = Review.objects.filter(
            user=user, app=app
        ).count()
        is_suspicious = review_count_by_user_for_app >= 3

        # Create review
        review = Review.objects.create(
            user=user,
            app=app,
            comment=comment,
            rating=rating,
            sentiment=sentiment_label,
            sentiment_score=sentiment_score,
            ip_address=ip_address,
            is_fake=is_suspicious
        )

        # Log suspicious review for admin review
        if is_suspicious:
            AdminReviewLog.objects.create(
                app=app,
                admin=None,               # can be assigned later
                review=review,
                action="Fake Review Detected (Multiple Reviews from same user)"
            )

        messages.success(request, "Review submitted successfully.")
        return redirect('app_details', app_id=app.id)

    # GET → show form
    return render(request, 'add_review.html', {'app': app})


# ────────────────────────────────────────────────
#                 PROFILE MANAGEMENT
# ────────────────────────────────────────────────

def edit_profile(request):
    """
    Lets the user update their profile (including avatar if form supports files).
    """
    if 'user_id' not in request.session:
        messages.error(request, "You need to log in first.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, user_id=request.session['user_id'])

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user,
    })


# ────────────────────────────────────────────────
#                     FEEDBACK
# ────────────────────────────────────────────────

def add_feedback(request):
    """
    Simple feedback form for logged-in users.
    """
    if 'user_id' not in request.session:
        messages.error(request, "You need to login first.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, user_id=request.session['user_id'])

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = user
            feedback.save()
            messages.success(request, "Thank you! Your feedback has been submitted.")
            return redirect('dashboard')
    else:
        form = FeedbackForm()

    return render(request, 'add_feedback.html', {
        'form': form,
        'user': user
    })