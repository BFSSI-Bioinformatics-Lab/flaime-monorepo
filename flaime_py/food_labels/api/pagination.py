from rest_framework.pagination import PageNumberPagination


class StoreProductSearchPagination(PageNumberPagination):
    """Pagination for POST /api/storeproducts/search/.

    Applied per-action (instantiated inside the ``search`` action) rather than
    as a project-wide default, so the plain ``/api/storeproducts/`` list and the
    other viewsets keep their current unpaginated response shape.

    ``page`` / ``page_size`` are read from the JSON request body (that is where
    the frontend puts them), falling back to the usual query parameters.
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_page_number(self, request, paginator):
        if isinstance(request.data, dict) and request.data.get("page"):
            return request.data["page"]
        return super().get_page_number(request, paginator)

    def get_page_size(self, request):
        if isinstance(request.data, dict) and request.data.get("page_size"):
            try:
                size = int(request.data["page_size"])
            except (TypeError, ValueError):
                return super().get_page_size(request)
            return max(1, min(size, self.max_page_size))
        return super().get_page_size(request)
