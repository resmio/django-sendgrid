# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
import django


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table(u'sendgrid_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'],
                                                                                   null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
        ))
        db.send_create_signal(u'sendgrid', ['Email'])

        if django.VERSION[0] == 1 and django.VERSION[1] > 4:
            # Adding index on 'Email', fields ['content_type', 'object_id']
            db.create_index(u'sendgrid_email', ['content_type_id', 'object_id'])

    @staticmethod
    def backwards(orm):
        if django.VERSION[0] == 1 and django.VERSION[1] > 4:
            # Removing index on 'Email', fields ['content_type', 'object_id']
            db.delete_index(u'sendgrid_email', ['content_type_id', 'object_id'])

        # Deleting model 'Email'
        db.delete_table(u'sendgrid_email')

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sendgrid.email': {
            'Meta': {'object_name': 'Email', 'index_together': "[['content_type', 'object_id']]"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['sendgrid']
