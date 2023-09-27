from django.db import models
from django.utils import timezone

# Create your models here.


class CustomerValidator(models.Manager):

    def customer_validator(self, post_data):
        """
        Valida los datos del cliente.

        Args:
            post_data (dict): Datos enviados mediante una solicitud POST.

        Returns:
            dict: Un diccionario que contiene errores encontrados durante la 
            validación.
        """

        errors = {}

        if len(post_data['first_name']) < 4:
            errors['first_name'] = 'Minimo 3 caracteres para nombre de usuario'
        if len(post_data['phone_number']) < 6:
            errors['phone_number'] = 'Minimo 6 digitos para numero de teléfono'

        return errors


class Customer(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=150, null=True)
    document = models.CharField(max_length=150, null=True)
    address = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomerValidator()


class ProductValidator(models.Manager):

    def product_validator(self, post_data):
        """
        Valida los datos del producto.

        Args:
            post_data (dict): Datos enviados mediante una solicitud POST.

        Returns:
            dict: Un diccionario que contiene errores encontrados durante la 
            validación.
        """

        errors = {}

        if len(post_data['name']) < 3:
            errors['name'] = 'Minimo 3 caracteres para nombre del producto'

        return errors


class Product(models.Model):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProductValidator()

    def __str__(self) -> str:
        """
        Devuelve una representación en forma de cadena del objeto Producto.

        Returns:
            str: Representación en forma de cadena del objeto Producto.
        """
        return f"Producto {self.name}"


class OrderValidator(models.Manager):

    def order_validator(self, post_data):
        """
        Valida los datos del pedido.

        Args:
            post_data (dict): Datos enviados mediante una solicitud POST.

        Returns:
            dict: Un diccionario que contiene errores encontrados durante la 
            validación.
        """

        errors = {}

        if post_data['product_id'] == 'Lista de productos':
            errors['product_id'] = 'Elige un producto para el pedido'
        if post_data['customer_id'] == 'Lista de clientes':
            errors['customer_id'] = 'Elige un cliente para el pedido'
        if int(post_data['amount']) <= 0:
            errors['amount'] = 'Introducir cantidad'
        if len(post_data['price']) < 4:
            errors['price'] = 'Introducir precio'

        return errors


class Order(models.Model):

    observation = models.CharField(max_length=255, null=True)
    amount = models.SmallIntegerField()
    price = models.CharField(max_length=255)
    deadline = models.DateField()
    delivered = models.DateField(null=True, blank=True)
    bill = models.CharField(max_length=15, null=True)
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="orders", on_delete=models.CASCADE)
    objects = OrderValidator()

    def deliver_product(self):
        """
        Marca el pedido como entregado o no entregado.

        Si el pedido ya ha sido entregado, se marca como no entregado.
        Si el pedido aún no ha sido entregado, se marca como entregado y se guarda la fecha actual.

        """

        if self.delivered == None:
            self.delivered = timezone.now()
            self.save()
        else:
            self.delivered = None
            self.save()


    def calculate_total_price(self):
        """
        Calcula el precio total del pedido.

        Returns:
            int: El precio total del pedido.
        """
        
        return int(self.price) * self.amount
