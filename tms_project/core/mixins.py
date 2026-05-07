from django.utils.cache import add_never_cache_headers


class NoCacheMixin:

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        add_never_cache_headers(response)

        return response