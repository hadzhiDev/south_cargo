from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.filters import DateFieldListFilter
from django.conf import settings

from whatsapp_api_client_python import API

from cargo.models import Load, Client, ClientBatchImport
from cargo.filters import DateFilter

greenAPI = API.GreenAPI(
    settings.GREEN_API_ID, settings.GREEN_API_TOKEN
)

@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('code', 'kilo', 'date', 'client', 'sent_to_client')
    list_filter = (DateFilter,) 
    search_fields = ('code', 'kilo', 'date', 'client')
    actions = ['send_to_whatsapp']
    readonly_fields = ('sent_to_client',)
    autocomplete_fields = ['client']

    @admin.action(description="📩 Отправить выбранные грузы в WhatsApp")
    def send_to_whatsapp(self, request, queryset):
        successful_count = 0
        failed_count = 0

        for load in queryset:
            if load.client and load.client.whatsapp_chat_id:
                client = load.client
                chat_id = client.whatsapp_chat_id

                message = f"""👋 Ассалоому Алейкум, урматтуу кардар {client.code}, {load.date} Складка түшкөн жүк келди! \n
🔢 Код: {load.code} \n
💰 Төлөм: {load.price} сом \n        
📍 Биздин дарек: Масалиева 46а, болжол Келечек базары
🕙 10:00 - 17:30 га чейин алып кетсеңиз болот
🤝 Урматтоо менен, ЮГ Карго \n 
📞 Тел: 0550 68 69 61"""

                response = greenAPI.sending.sendMessage(chat_id, message)
                # 📅 Дата прибытия: {load.date}\n⚖️ Масса: {load.kilo} кг\n От вас: {load.price} 
                if response.code == 200:
                    load.sent_to_client = True
                    load.save()
                    successful_count += 1
                else:
                    failed_count += 1

        self.message_user(
            request,
            f"✅ Успешно отправлено: {successful_count}. ❌ Ошибки: {failed_count}",
            messages.SUCCESS if successful_count else messages.ERROR
        )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code', 'wa_number', 'name')
    list_filter = ('code', 'wa_number', 'name')
    search_fields = ('code', 'wa_number', 'name')


@admin.register(ClientBatchImport)
class ClientBatchImportAdmin(admin.ModelAdmin):
    list_display = ("id",)
    
    def save_model(self, request, obj, form, change):
        obj.save()  # Calls the overridden `save()` method in the model
        self.message_user(request, "✅ Клиенты успешно загружены!")
