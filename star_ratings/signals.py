def calculate_ratings(sender, instance, **kwargs):
    instance.aggregate.calculate()
