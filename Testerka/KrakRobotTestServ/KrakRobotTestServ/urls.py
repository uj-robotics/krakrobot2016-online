from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    # url(r'^$', 'KrakRobotTestServ.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^', include('KrakRobotTestServ.uploader.urls')),
    url(r'^up/$', RedirectView.as_view(url='/uploader/list/')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="index"),
    url(r'^rank/$', TemplateView.as_view(template_name='coding/rank.html'), name="rank"),
    url(r'^your_codes/$', TemplateView.as_view(template_name='coding/your_codes.html'), name="your_codes"),
) + static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
