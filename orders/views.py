from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Customer, Order, Product

# Create your views here.


# --Balance--
def index(request):
    """
    Vista para mostrar todos los pedidos en una página de balance.

    Args:
        request (HttpRequest): La solicitud HTTP recibida por el servidor.

    Returns:
        HttpResponse: La respuesta HTTP que muestra todos los pedidos en una 
        página de balance.
    """

    # Recupera todos los pedidos
    orders = Order.objects.all()

    context = {
        'all_orders': orders,
    }

    # Renderiza 'balance_sheets/all.html' utilizando el diccionario context.
    return render(request, 'balance_sheets/all.html', context)


def to_deliver_balance(request):
    """
    Vista para mostrar todos los pedidos que aún no se han entregado en una 
    página de balance.

    Args:
        request (HttpRequest): La solicitud HTTP recibida por el servidor.

    Returns:
        HttpResponse: La respuesta HTTP que muestra todos los pedidos que aún 
        no se han entregado en una página de balance.
    """

    # Recupera los pedidos que no se han entregado
    to_deliver = Order.objects.filter(delivered__isnull=True)

    context = {
        'to_deliver': to_deliver
    }

    # Renderiza 'balance_sheets/to_deliver.html' utilizando el diccionario context.
    return render(request, 'balance_sheets/to_deliver.html', context)


def delivered_balance(request):
    """
    Vista para mostrar todos los pedidos que han sido entregadas en una página
    de balance.

    Args:
        request (HttpRequest): La solicitud HTTP recibida por el servidor.

    Returns:
        HttpResponse: La respuesta HTTP que muestra todos los pedidos que han
        sido entregadas en una página de balance.
    """

    # Obtener todos los pedidos entregados
    delivered = Order.objects.filter(delivered__isnull=False)

    context = {
        'delivered_orders': delivered
    }

    # Renderiza 'delivered.html' utilizando el diccionario context.
    return render(request, 'balance_sheets/delivered.html', context)


# Pedidos
def order_form(request):
    """
    Renderiza el formulario de creación de un pedido.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: La respuesta HTTP que renderiza el formulario de creación
        de un pedido.

    """

    # Obtener todos los clientes y productos para pasarlos como contexto
    context = {
        'customers': Customer.objects.all(),
        'products': Product.objects.all()
    }

    # Renderiza 'orders/add.html' utilizando el diccionario context.
    return render(request, 'orders/add.html', context)


def process_new_order(request):
    """
    Procesa la creación de un nuevo pedido.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponseRedirect: Una redirección a la vista "index".

    """

    # Obtener los datos del formulario enviado
    data = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Order.objects.order_validator(data)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para crear un pedido.
        return redirect(reverse('order_form'))

    # Obtener el producto y cliente correspondiente a los IDs proporcionados
    product = Product.objects.get(id=data['product_id'])
    customer = Customer.objects.get(id=data['customer_id'])

    # Crear el pedido con los datos proporcionados
    Order.objects.create(
        product=product,
        customer=customer,
        observation=data['observation'],
        amount=data['amount'],
        price=data['price'],
        deadline=data['deadline'],
        bill=data['bill']
    )

    # Crear un mensaje de exito.
    messages.success(request, 'Pedido agregado a la lista')

    # Redireccionar a la vista "index".
    return redirect(reverse(index))


def edit_order_form(request, id):
    """
    Muestra el formulario de edición de una orden existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del pedido a editar.

    Returns:
        HttpResponse: La respuesta HTTP que muestra el formulario de edición.

    """

    # Obtener el pedido a editar utilizando el ID proporcionado
    to_edit_order = Order.objects.get(id=id)

    # Formatear la fecha limite para que sea legible por el HTML
    formated_date = to_edit_order.deadline.strftime("%Y-%m-%d")

    # Crear un context con los clientes, productos y la orden a editar
    context = {
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'order': to_edit_order,
        'deadline_formated': formated_date
    }

    # Renderizar el template donde se van a editar los datos
    return render(request, 'orders/edit.html', context)


def process_order_edit(request, id):
    """
    Procesa la edición de una orden existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del pedido a editar.

    Returns:
        HttpResponseRedirect: Una redirección a la página de índice.

    """

    # Obtener la orden a editar utilizando el ID proporcionado
    to_edit = Order.objects.get(id=id)

    # Obtener los nuevos datos enviados en el cuerpo de la solicitud POST
    new_data = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Order.objects.order_validator(new_data)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para editar el pedido.
        return redirect(reverse('edit_order_form', args=[id]))

    # Pasar a enteros los datos nuevos del formulario
    product_id = int(new_data['product_id'])
    customer_id = int(new_data['customer_id'])

    # Obtener los objetos de producto y cliente con los nuevos datos
    product = Product.objects.get(id=product_id)
    customer = Customer.objects.get(id=customer_id)

    # Actualizar datos del pedido a editar
    to_edit.product = product
    to_edit.customer = customer
    to_edit.observation = new_data['observation']
    to_edit.amount = new_data['amount']
    to_edit.price = new_data['price']
    to_edit.deadline = new_data['deadline']
    to_edit.bill = new_data['bill']

    # Guardar los cambios
    to_edit.save()

    # Crea mensaje informando la acción
    messages.warning(request, 'Pedido modificado')

    # Redirigir al índie de pedidos
    return redirect(reverse(index))


def delete_order(request, id):
    """
    Elimina un pedido existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del pedido a eliminar.

    Returns:
        HttpResponseRedirect: Una redirección a la página de índice.

    """

    # Obtener el pedido a eliminar
    to_delete = Order.objects.get(id=id)

    # Eliminar el pedido
    to_delete.delete()

    # Crea mensaje informando la acción.
    messages.error(request, 'Pedido eliminado a la lista')

    # Redirigir al índice de pedidos
    return redirect(reverse(index))


def order_detail(request, id):
    """
    Muestra los detalles de un pedido específico.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del pedido a mostrar.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza el template 
        'orders/detail.html',con el contexto que contiene el pedido 
        especificado.

    """

    # Obtener el pedido y pasarlo como contexto
    context = {
        'order': Order.objects.get(id=id)
    }

    # Renderizar template detail.html de la carpeta orders con el contexto
    return render(request, 'orders/detail.html', context)


def order_delivered(request, id):
    """
    Marca un pedido como entregado o como no entregado y redirige al índice.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del peido a marcar.

    Returns:
        HttpResponseRedirect: Una respuesta HTTP que redirige al índice.

    """

    # Obtener el pedido utilizando el ID proporcionado
    order = Order.objects.get(id=id)

    # Marcar o desmarcar como entregado con el metodo deliver_product()
    order.deliver_product()

    # Redirigir al índice
    return redirect(reverse(index))


# --Clientes--
def customers(request):
    """
    Muestra todos los clientes y renderiza la plantilla 'index.html'.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la plantilla 'index.html' 
        con todos los clientes.

    """
    # Obtener todos los clientes
    all_customers = Customer.objects.all()

    # Crear un contexto usando todos los clientes obtenidos
    context = {'all_customers': all_customers}

    # Renderizar index con el contexto proporcionado
    return render(request, 'customers/index.html', context)


def customer_form(request):
    """
    Renderiza la plantilla 'add.html' que muestra un formulario para agregar 
    un cliente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Una respuesta HTTP que muestra la plantilla 'add.html'.

    """

    # Renderizar la plantilaa 'add.html'
    return render(request, 'customers/add.html')


def process_new_customer(request):
    """
    Procesa los datos del formulario enviado por POST para agregar un nuevo 
    cliente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponseRedirect: Una redirección 'customers'.

    """
    form = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Customer.objects.customer_validator(form)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para crear el cliente.
        return redirect(reverse('client_form'))

    Customer.objects.create(
        first_name=form['first_name'],
        last_name=form['last_name'],
        phone_number=form['phone_number'],
        email=form['email'],
        document=form['document'],
        address=form['address']
    )

    # Crea mensaje informando la acción
    messages.success(request, 'Cliente agregado a la lista')

    # Redirigir a la página que rendeiza customers
    return redirect(reverse('customers'))


def customer_edit_form(request, id):
    """
    Muestra un formulario de edición para modificar los datos de un cliente 
    existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del cliente a editar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página de edición del 
        cliente.
    """

    # Contexto con los datos del cliente a editar
    context = {
        'customer': Customer.objects.get(id=id)
    }

    # Renderiza formulario de edición con el contexto
    return render(request, 'customers/edit.html', context)


def customer_edit_process(request, id):
    """
    Procesa la información enviada desde el formulario de edición y actualiza 
    los datos del cliente correspondiente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del cliente a editar.

    Returns:
        HttpResponseRedirect: Una redirección a la página de lista de clientes.

    """

    # Obtener el objeto Customer con el ID proporcionado
    edit_customer = Customer.objects.get(id=id)

    # Obtener los datos del formulario
    form_data = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Customer.objects.customer_validator(form_data)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para editar el cliente.
        return redirect(reverse('customer_edit_form', args=[id]))

    # Actualizar los datos del cliente
    edit_customer.first_name = form_data['first_name']
    edit_customer.last_name = form_data['last_name']
    edit_customer.phone_number = form_data['phone_number']
    edit_customer.email = form_data['email']
    edit_customer.document = form_data['document']
    edit_customer.address = form_data['address']

    # Guardar los cambios
    edit_customer.save()

    # Crea mensaje informando la acción
    messages.warning(request, 'Cliente modificado')

    # Redirigar a customers
    return redirect(reverse(customers))


def delete_customer(request, id):
    """
    Elimina un cliente de la base de datos.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del cliente a eliminar.

    Returns:
        HttpResponseRedirect: Una redirección a la página de lista de clientes.

    """

    # Obtener el cliente a editar
    customer_to_delete = Customer.objects.get(id=id)

    # Eliminar cliente
    customer_to_delete.delete()

    # Crea mensaje informando la acción
    messages.error(request, 'Cliente eliminado a la lista')

    # Redirigir a customers
    return redirect(reverse(customers))


# --Productos--
def products(request):
    """
    Muestra la página de productos con una lista de todos ellos.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página HTML de 
        productos.

    """

    # Obtener todos los productos
    all_products = Product.objects.all()

    # Crear un diccionario contexto con todos los productos
    context = {'all_products': all_products}

    # Renderizar el inicio de productos con el contexto
    return render(request, 'products/index.html', context)


def product_form(request):
    """
    Muestra el formulario para añadir un producto.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página HTML del 
        formulario de productos.

    """

    # Renderiza formulario para añadir producto
    return render(request, 'products/add.html')


def process_new_product(request):
    """
    Procesa la información del formulario y crea un nuevo producto en la base 
    de datos.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponseRedirect: Una respuesta HTTP que redirige a la página de 
        productos.

    """

    # Obtener los datos del formulario
    data = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Product.objects.product_validator(data)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para crear el producto.
        return redirect(reverse('product_form'))

    # Crear el producto con los datos obtenidos
    Product.objects.create(name=data['name'], description=data['description'])

    # Crea mensaje informando la acción
    messages.success(request, 'Producto agregado a la lista')

    # Redirigr a 'prodcuts'
    return redirect(reverse('products'))


def product_edit_form(request, id):
    """
    Muestra el formulario de edición de un producto existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del producto a editar.

    Returns:
        HttpResponse: Una respuesta HTTP con el formulario de edición.

    """

    # Crea contexto con el producto a editar
    context = {
        'product': Product.objects.get(id=id)
    }

    # Redirige al formulario para editar con el contexto
    return render(request, 'products/edit.html', context)


def product_edit_process(request, id):
    """
    Procesa la edición de un producto existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del producto a editar.

    Returns:
        HttpResponseRedirect: Una respuesta HTTP que redirecciona a la página
        de productos.

    """

    # Obtener el producto a editar
    edit_product = Product.objects.get(id=id)

    # Obtener los datos nuevos
    form_data = request.POST

    # Validar los datos que se entregaron en el formulario
    errors = Product.objects.product_validator(form_data)

    # Si se encuentran errores se crean mensajes con los mismos
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        # Redirige al formulario para editar el producto.
        return redirect(reverse('product_edit_form', args=[id]))

    # Actualizar los datos del producto
    edit_product.name = form_data['name']
    edit_product.description = form_data['description']

    # Guardar los cambios
    edit_product.save()

    # Crea mensaje informando la acción
    messages.warning(request, 'Producto modificado')

    # Redirigir a 'products'
    return redirect(reverse(products))


def delete_product(request, id):
    """
    Elimina un producto existente.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del producto a eliminar.

    Returns:
        HttpResponseRedirect: Una respuesta HTTP que redirecciona a la 
        página de productos.

    """

    # Obtener producto a eliminar
    customer_to_delete = Product.objects.get(id=id)

    # Eliminar producto
    customer_to_delete.delete()

    # Crea mensaje informando la acción.
    messages.error(request, 'Producto eliminado a la lista')

    # Redirigr a products
    return redirect(reverse(products))
