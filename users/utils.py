from xhtml2pdf import pisa
from io import BytesIO
from django.core.mail import EmailMessage

def enviar_factura_por_correo(order):
    total = 0
    items_html = ""
    for item in order.items.all():
        subtotal = item.quantity * item.product.price
        total += subtotal
        items_html += f"""
            <tr>
                <td>{item.product.name}</td>
                <td>{item.size.name}</td>
                <td>{item.quantity}</td>
                <td>${item.product.price:.2f}</td>
                <td>${subtotal:.2f}</td>
            </tr>
        """

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 40px;
                color: #333;
            }}
            .header {{
                display: flex;
                align-items: center;
                border-bottom: 2px solid #e4e4e4;
                padding-bottom: 10px;
                margin-bottom: 0;
            }}
            .logo {{
                height: 250px;
                margin-right: 20px;
            }}
            .title {{
                font-size: 30px;
            }}
            .info {{
                font-size: 20px;
                margin-bottom: 20px;
            }}
            .info p {{
                margin: 4px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                 font-size: 15px;
            }}
            th {{
                background-color: #2980BA;
                color: #000;
                padding: 5px;
                border: 1px solid #ccc;
            }}
            td {{
                padding: 5px;
                border: 1px solid #ddd;
            }}
            .total {{
                text-align: right;
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="media/logo.png" alt="Moda Chic Logo" class="logo">
        </div>

        <h2 class="title">Factura de compra</h2>

        <div class="info">
            <p><strong>Pedido #:</strong> {order.id}</p>
            <p><strong>Cliente:</strong> {order.nombre}</p>
            <p><strong>Email:</strong> {order.email}</p>
            <p><strong>Teléfono:</strong> {order.telefono}</p>
            <p><strong>Dirección:</strong> {order.direccion}</p>
            <p><strong>Fecha:</strong> {order.created_at.strftime('%Y-%m-%d')}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Talla</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        <p class="total">Total: ${total:.2f}</p>
    </body>
    </html>
    """


    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if not pisa_status.err:
        email = EmailMessage(
            subject=f"Factura de tu pedido #{order.id}",
            body="Gracias por tu compra. Adjuntamos tu factura.",
            from_email="ventas@modachic.com",
            to=[order.email],
        )
        email.attach(f"Factura_ModaChic_{order.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
        email.send()
    else:
        print("Error generando el PDF")
