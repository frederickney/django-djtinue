from django.conf import settings
from django.utils.dates import MONTHS
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404

from djtinue.admissions.application.models import Application
from djtinue.admissions.application.forms import (
    ApplicationForm, ContactForm, EducationForm, EducationRequiredForm,
    OrderForm,
)
from djtools.fields import STATE_CHOICES
from djtools.utils.mail import send_mail
from djforms.processors.models import Order
from djforms.processors.forms import TrustCommerceForm

import os

REQ = False
PROGRAM = {
    'bdi': 'Master (MSc) in Business Design &amp; Innovation Application',
    'bsm': 'Master (MSc) in Business Sports Management Application',
    'bsn': 'RSN to BSN',
    'music': 'M.M. in Music Theatre Vocal Pedagogy',
}
SUBJECT = "Application for Carthage"


def form(request, slug=None):

    if settings.DEBUG:
        TO_LIST = [settings.SERVER_MAIL,]
    else:
        TO_LIST = settings.ADMISSIONS_EMAILS['default']
        # this will throw an error if someone uses a slug that does
        # not exist, which is fine for now
        if slug:
            TO_LIST = settings.ADMISSIONS_EMAILS[slug]


    # templates for email and success page
    p = 'admissions/application/'
    if slug:
        p = os.path.join(p, slug)
    form_template = '{}/form.html'.format(p)
    email_template = '{}/email.html'.format(p)

    if request.method=='POST':

        form_app = ApplicationForm(
            request.POST,
            request.FILES,
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ct1 = ContactForm(
            request.POST,
            prefix='ct1',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ct2 = ContactForm(
            request.POST,
            prefix='ct2',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ed1 = EducationRequiredForm(
            request.POST,
            request.FILES,
            prefix='ed1',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ed2 = EducationForm(
            request.POST,
            request.FILES,
            prefix='ed2',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ed3 = EducationForm(
            request.POST,
            request.FILES,
            prefix='ed3',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ed4 = EducationForm(
            request.POST,
            request.FILES,
            prefix='ed4',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ed5 = EducationForm(
            request.POST,
            request.FILES,
            prefix='ed5',
            label_suffix='',
            use_required_attribute=REQ,
        )
        form_ord = OrderForm(
            request.POST,
            label_suffix='',
            use_required_attribute=REQ,
            initial={'total':35, 'avs':False,'auth':'sale'},
        )
        form_proc = TrustCommerceForm(
            request.POST,
            label_suffix='',
            use_required_attribute=False,
        )
        if form_app.is_valid() and form_ct1.is_valid() and form_ct2.is_valid()\
          and form_ed1.is_valid() and form_ord.is_valid():

            app = form_app.save()
            app.slug = slug
            app.social_security_four = app.social_security_number[-4:]
            app.save()
            # recommendations
            ct1 = form_ct1.save(commit=False)
            ct1.application = app
            ct1.save()
            ct2 = form_ct2.save(commit=False)
            ct2.application = app
            ct2.save()
            # schools
            ed1 = form_ed1.save(commit=False)
            ed1.application = app
            ed1.save()
            ed2 = form_ed2.save(commit=False)
            ed2.application = app
            ed2.save()
            ed3 = form_ed3.save(commit=False)
            ed3.application = app
            ed3.save()
            ed4 = form_ed4.save(commit=False)
            ed4.application = app
            ed4.save()
            ed5 = form_ed5.save(commit=False)
            ed5.application = app
            ed5.save()
            # transaction
            order = form_ord.save()
            order.total = 35.00
            order.operator = settings.TC_OPERATOR
            subject = '{} {}: ({}, {})'.format(
                SUBJECT, PROGRAM[slug], app.last_name, app.first_name
            )
            if app.payment_method == 'Credit Card':

                form_proc = TrustCommerceForm(
                    order, app, request.POST, use_required_attribute=False
                )

                if form_proc.is_valid():
                    r = form_proc.processor_response
                    order.status = r.msg['status']
                    order.transid = r.msg['transid']
                    order.cc_name = form_proc.name
                    order.cc_4_digits = form_proc.card[-4:]
                    order.save()
                    app.order.add(order)
                    order.app = app
                    sent = send_mail(
                        request, TO_LIST, subject, app.email, email_template,
                        order,
                    )
                    order.send_mail = sent
                    order.save()

                    return HttpResponseRedirect(
                        reverse(
                            'admissions_application_success',
                            kwargs={'slug':slug},
                        )
                    )

                else:
                    r = form_proc.processor_response
                    if r:
                        order.status = r.status
                    else:
                        order.status = 'Form Invalid'
                    order.cc_name = form_proc.name
                    if form_proc.card:
                        order.cc_4_digits = form_proc.card[-4:]
                    order.save()
                    app.order.add(order)
            else:
                order.auth='COD'
                order.status='Pay later'
                order.save()
                app.order.add(order)
                # used for email rendering
                order.app = app
                sent = send_mail(
                    request, TO_LIST, subject, app.email, email_template,
                    order,
                )
                order.send_mail = sent
                order.save()
                return HttpResponseRedirect(
                    reverse(
                        'admissions_application_success',
                        kwargs={'slug':slug},
                    )
                )
        else:
            if request.POST.get('payment_method') == 'Credit Card':
                form_proc = TrustCommerceForm(
                    None, request.POST, use_required_attribute=False
                )
                form_proc.is_valid()
            else:
                form_proc = TrustCommerceForm(use_required_attribute=False)
    else:
        form_app = ApplicationForm(
            label_suffix='', use_required_attribute=REQ
        )
        form_ct1 = ContactForm(
           prefix='ct1',  label_suffix='', use_required_attribute=REQ
        )
        form_ct2 = ContactForm(
           prefix='ct2',  label_suffix='', use_required_attribute=REQ
        )
        form_ed1 = EducationRequiredForm(
            prefix='ed1', label_suffix='', use_required_attribute=REQ
        )
        form_ed2 = EducationForm(
            prefix='ed2', label_suffix='', use_required_attribute=REQ
        )
        form_ed3 = EducationForm(
            prefix='ed3', label_suffix='', use_required_attribute=REQ
        )
        form_ed4 = EducationForm(
            prefix='ed4', label_suffix='', use_required_attribute=REQ
        )
        form_ed5 = EducationForm(
            prefix='ed5', label_suffix='', use_required_attribute=REQ
        )
        form_ord = OrderForm(
            label_suffix='', use_required_attribute=REQ,
            initial={'total':35, 'avs':False,'auth':'sale'}
        )
        form_proc = TrustCommerceForm(
            label_suffix='', use_required_attribute=False
        )

    extra_context = {
        'form_app': form_app,
        'form_ct1': form_ct1,
        'form_ct2': form_ct2,
        'form_ord': form_ord,
        'form_ed1': form_ed1,
        'form_ed2': form_ed2,
        'form_ed3': form_ed3,
        'form_ed4': form_ed4,
        'form_ed5': form_ed5,
        'form_proc': form_proc,
        'slug': slug,
    }

    return render(request, form_template, extra_context)


@login_required
def detail(request, aid):
    data = get_object_or_404(Application, pk=aid)
    return render(
        request, 'admissions/application/email.html',
        {'data': {'app':data,},}
    )


def success(request, slug):
    """Redirect here after user submits application form."""
    template = 'admissions/application/done.html'
    return render(request, template, {'slug':slug})
