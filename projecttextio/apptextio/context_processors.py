from .models import Order,OrderItem

def no_of_orderitms(request):
    numbers = 0
    try:
        order = Order.objects.filter(user=request.user,isordered=False,from_buynow=False).first()
        if order:
            orderitems = OrderItem.objects.filter(user=request.user,order_id=order)
            numbers = orderitems.count()
        return {"numbers":numbers}
    except:
        return {"numbers":numbers}