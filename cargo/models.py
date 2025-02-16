from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class ClientBatchImport(models.Model):
    class Meta:
        verbose_name = 'Импорт клиентских партий'
        verbose_name_plural = 'Импорт клиентских партий'

    clients_text = models.TextField(verbose_name="Список клиентов")

    def save(self, *args, **kwargs):
        """
        When saving, process the clients_text field and create Client objects.
        """
        lines = self.clients_text.strip().split("\n")
        created_count = 0
        existing_count = 0

        for line in lines:
            parts = line.strip().split("+", 1)  # Split by the first "+"
            if len(parts) == 2:
                code = parts[0].strip()
                wa_number = "+" + parts[1].replace(" ", "").strip()

                # Check if client already exists
                client, created = Client.objects.get_or_create(code=code, wa_number=wa_number)
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        super().save(*args, **kwargs)

        print(f"✅ {created_count} clients added, 🔄 {existing_count} already existed.")  # Log in console


class Load(models.Model):
    class Meta:
        verbose_name = 'Груз'
        verbose_name_plural = 'Грузы'

    code = models.CharField(max_length=200, verbose_name='код', null=True, blank=True)
    date = models.DateField(verbose_name='дата')
    kilo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='кг', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена', null=True, blank=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='клиент', related_name='loads')
    sent_to_client = models.BooleanField(default=False, verbose_name='отправлено клиенту')

    def __str__(self):
        return f'{self.code} - {self.date}'


class Client(models.Model):
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    name = models.CharField(max_length=300, null=True, blank=True)
    code = models.CharField(max_length=200, verbose_name='код', blank=True, null=True)
    wa_number = PhoneNumberField(max_length=100, unique=True, verbose_name='номер WhatsApp', blank=True, null=True)

    def __str__(self):
        return f'{self.code} - {self.wa_number} - {self.name}'
    
    @property
    def whatsapp_chat_id(self):
        """Convert WhatsApp number to GreenAPI Chat ID format."""
        if self.wa_number:
            phone_str = str(self.wa_number).replace('+', '').replace(' ', '')
            return f"{phone_str}@c.us"
        return None
