from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from recipe.models import IngredientAmount
from io import BytesIO


def download_shopping_list(request):
    ingredients = IngredientAmount.objects.filter(
        recipe__purchases__user=request.user).values_list(
        'ingredient__name', 'ingredient__measurement_unit',
        'amount')
    shopping_list = {}
    for item in ingredients:
        name = item[0]
        if name not in shopping_list:
            shopping_list[name] = {
                'measurement_unit': item[1],
                'amount': item[2]}
        else:
            shopping_list[name]['amount'] += item[2]
    height = 700
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('arial', 'static/arial.ttf'))
    page = canvas.Canvas(buffer)
    page.setFont('arial', 13)
    page.drawString(200, 800, "Список покупок")
    for i, (name, data) in enumerate(shopping_list.items(), 1):
        page.drawString(75, height, (f"<{i}> {name} - {data['amount']}, "
                                     f"{data['measurement_unit']}"))
        height -= 25
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='shopping_list.pdf'
    )
