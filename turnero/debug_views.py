from django.urls import get_resolver
from django.shortcuts import render

def url_index(request):
    resolver = get_resolver()
    patterns = []

    def extract_patterns(urlpatterns, prefix=""):
        for entry in urlpatterns:
            if hasattr(entry, "url_patterns"):  # included urls
                extract_patterns(entry.url_patterns, prefix + str(entry.pattern))
            else:
                try:
                    patterns.append({
                        "pattern": prefix + str(entry.pattern),
                        "name": entry.name,
                        "callback": entry.callback.__module__ + "." + entry.callback.__name__,
                    })
                except Exception:
                    patterns.append({
                        "pattern": prefix + str(entry.pattern),
                        "name": entry.name,
                        "callback": None,
                    })

    extract_patterns(resolver.url_patterns)

    return render(request, "url_index.html", {"patterns": patterns})
