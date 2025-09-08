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
            @page {{
                size: A4;
                margin: 40px;
            }}
            body {{
                font-family: 'Helvetica', sans-serif;
                color: #333;
            }}
            .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            .logo {{
                height: 120px;
            }}
            .company-info {{
                text-align: right;
                font-size: 12px;
            }}
            .title {{
                font-size: 24px;
                margin-top: 30px;
                margin-bottom: 30px;
                text-align: center;
                color: #b76e79;
            }}
            .info {{
                font-size: 14px;
                margin-top: 20px;
                line-height: 1.1;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 13px;
            }}
            th {{
                background-color: #f8e1e7;
                color: #000;
                padding: 8px;
                border: 1px solid #ccc;
                text-align: left;
            }}
            td {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            .total-box {{
                margin-top: 30px;
                text-align: right;
                font-size: 16px;
                font-weight: bold;
                border-top: 2px solid #333;
                padding-top: 10px;
            }}
            .footer {{
                margin-top: 40px;
                font-size: 12px;
                text-align: center;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="media/logo.png" alt="Moda Chic Logo" class="logo">
            <div class="company-info">
                <strong>Moda Chic</strong><br>
                ventas@modachic.com<br>
                www.modachic.com
            </div>
        </div>

        <h2 class="title">Factura de compra</h2>

        <div class="info">
            <p><strong>Pedido #:</strong> {order.id}</p>
            <p><strong>Cliente:</strong> {order.nombre}</p>
            <p><strong>Email:</strong> {order.email}</p>
            <p><strong>Teléfono:</strong> {order.telefono}</p>
            <p><strong>Departamento:</strong> {order.departamento}</p>
            <p><strong>Municipio:</strong> {order.ciudad}</p>
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

        <p class="total-box">
            Total: ${total:.2f}
        </p>

        <div class="footer">
            Gracias por comprar en <strong>Moda Chic</strong> 💖<br>
            Síguenos en Instagram @modachic o visita www.modachic.com
        </div>
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
