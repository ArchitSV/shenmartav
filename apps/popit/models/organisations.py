# -*- coding: utf-8 -*
# extended by Sebastian Henschel sebastiantransparency@gmail.com for
# http://shenmartav.ge

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models

from django_date_extensions.fields import ApproximateDateField
from markitup.fields import MarkupField

from popit.models import ModelBase, DataKey, Data, date_help_text, CodeType
from glt import slughifi



class Organisation(ModelBase):
    slug    = models.SlugField(max_length=300, editable=False)
    summary = models.TextField(null=True, blank=True, default='')
    started = ApproximateDateField(null=True, blank=True, help_text=date_help_text)
    ended   = ApproximateDateField(null=True, blank=True, help_text=date_help_text)

    class Meta:
        ordering = [ 'slug' ]
        app_label = 'popit'

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        try:
            return self.names.all()[0].name
        except:
            return 'Unknown'

    #@models.permalink
    #def get_absolute_url(self):
    #    return ( 'organisation', [ self.slug ] )

class OrganisationDataKey(DataKey):
    class Meta:
        app_label = 'popit'

class OrganisationData(Data):
    organisation = models.ForeignKey(Organisation, related_name='data')
    key = models.ForeignKey(OrganisationDataKey, related_name='values')
    class Meta:
        app_label = 'popit'
        verbose_name_plural = 'organisation data'

class OrganisationName(ModelBase):
    organisation = models.ForeignKey(Organisation, related_name='names')
    name        = models.CharField(max_length=300)
    main        = models.BooleanField()
    start_date  = ApproximateDateField(blank=True)
    end_date    = ApproximateDateField(blank=True)

    class Meta:
        ordering = [ '-main', '-start_date', 'end_date', 'name' ]
        app_label = 'popit'

    def save(self, *args, **kwargs):
        super(OrganisationName, self).save(*args, **kwargs)

        org = self.organisation

        if self.main == True:            
            # If we are main check that no other names for this org are            
            for name in org.names.filter(main=True).exclude(id=self.id):
                name.main = False
                name.save()

            # create the orgs slug based on our name
            org.slug = slughifi(self.name)
            org.save()
            
        else:
            # if there are no mained names set main on ourselves
            if org.names.filter(main=True).count() == 0:
                self.main = True
                self.save()

    def __unicode__(self):
        return self.name

class OrganisationCode(models.Model):
    organisation    = models.ForeignKey(Organisation, related_name='codes')
    type            = models.ForeignKey(CodeType)
    code            = models.CharField(max_length=100)

    class Meta:
        app_label = 'popit'

    def __unicode__(self):
        return u'%s (%s)' % (self.code, self.type)
