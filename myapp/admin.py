from django.contrib import admin
from .models import CustomerUser, Category, Application, Review, Feedback, AdminReviewLog

# --------------------------------------------------
# Customer User Admin
# --------------------------------------------------
@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'status', 'last_login', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('status', 'gender', 'country')
    readonly_fields = ('last_login', 'created_at', 'updated_at')

# --------------------------------------------------
# Category Admin
# --------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# --------------------------------------------------
# Application Admin
# --------------------------------------------------
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'rating', 'avg_sentiment_score', 'is_fraud', 'added_on')
    search_fields = ('name', 'category__name')
    list_filter = ('is_fraud', 'category')
    readonly_fields = ('avg_sentiment_score', 'added_on')

# --------------------------------------------------
# Review Admin
# --------------------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'app', 'rating', 'sentiment', 'sentiment_score', 'is_fake', 'created_at')
    search_fields = ('user__username', 'app__name', 'comment')
    list_filter = ('sentiment', 'is_fake', 'created_at')
    readonly_fields = ('sentiment_score', 'created_at', 'ip_address')

# --------------------------------------------------
# Feedback Admin
# --------------------------------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

# --------------------------------------------------
# Admin Review Log Admin
# --------------------------------------------------
@admin.register(AdminReviewLog)
class AdminReviewLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'app', 'admin', 'review', 'action', 'created_at')
    search_fields = ('app__name', 'admin__username', 'review__comment', 'action')
    list_filter = ('action', 'created_at')
    readonly_fields = ('created_at',)
