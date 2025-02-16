from django.contrib.admin import SimpleListFilter
from django.utils.timezone import now
from datetime import datetime, timedelta

class DateFilter(SimpleListFilter):
    title = 'Дата'
    parameter_name = 'date'  # Changed from 'date_time' to 'date'
    template = 'admin/filters/date_filter_calendar.html'

    def lookups(self, request, model_admin):
        return [
            ('today', 'Сегодня'),
            ('past_week', 'Последние 7 дней'),
            ('this_month', 'Этот месяц'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'today':
            return queryset.filter(date=now().date())
        elif value == 'past_week':
            return queryset.filter(date__gte=now().date() - timedelta(days=7))
        elif value == 'this_month':
            return queryset.filter(date__month=now().month)
        elif value:  # User-selected date
            try:
                selected_date = datetime.strptime(value, "%Y-%m-%d").date()
                return queryset.filter(date=selected_date)
            except ValueError:
                return queryset.none()  # Ignore invalid dates
        return queryset
