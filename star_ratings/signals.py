def calculate_ratings(sender, instance, **kwargs):
    instance.rating.calculate()
