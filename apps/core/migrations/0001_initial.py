# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        try:
            # Adding model 'Alias'
            db.create_table('core_alias', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='alias', null=True, to=orm['contenttypes.ContentType'])),
                ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ))
            db.send_create_signal('core', ['Alias'])

            # Adding model 'Road'
            db.create_table('core_road', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ))
            db.send_create_signal('core', ['Road'])

            # Adding model 'Node'
            db.create_table('core_node', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('road', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Road'])),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('latitude', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
                ('longitude', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
                ('position', self.gf('django.db.models.fields.SmallIntegerField')()),
            ))
            db.send_create_signal('core', ['Node'])

            # Adding unique constraint on 'Node', fields ['road', 'position']
            db.create_unique('core_node', ['road_id', 'position'])

            # Adding model 'Section'
            db.create_table('core_section', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('road', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Road'])),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
                ('start', self.gf('django.db.models.fields.related.ForeignKey')(related_name='start_section', to=orm['core.Node'])),
                ('end', self.gf('django.db.models.fields.related.ForeignKey')(related_name='end_section', to=orm['core.Node'])),
                ('direction', self.gf('django.db.models.fields.CharField')(max_length=1)),
                ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ))
            db.send_create_signal('core', ['Section'])

            # Adding unique constraint on 'Section', fields ['road', 'direction', 'position']
            db.create_unique('core_section', ['road_id', 'direction', 'position'])

            # Adding unique constraint on 'Section', fields ['road', 'direction', 'start']
            db.create_unique('core_section', ['road_id', 'direction', 'start_id'])

            # Adding unique constraint on 'Section', fields ['road', 'direction', 'end']
            db.create_unique('core_section', ['road_id', 'direction', 'end_id'])

            # Adding model 'Situation'
            db.create_table('core_situation', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'])),
                ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
                ('is_from_user', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('rating', self.gf('django.db.models.fields.SmallIntegerField')()),
                ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
                ('status_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
                ('reason', self.gf('django.db.models.fields.TextField')(blank=True)),
            ))
            db.send_create_signal('core', ['Situation'])
        except Exception, e:
            print e


    def backwards(self, orm):
        
        # Removing unique constraint on 'Section', fields ['road', 'direction', 'end']
        db.delete_unique('core_section', ['road_id', 'direction', 'end_id'])

        # Removing unique constraint on 'Section', fields ['road', 'direction', 'start']
        db.delete_unique('core_section', ['road_id', 'direction', 'start_id'])

        # Removing unique constraint on 'Section', fields ['road', 'direction', 'position']
        db.delete_unique('core_section', ['road_id', 'direction', 'position'])

        # Removing unique constraint on 'Node', fields ['road', 'position']
        db.delete_unique('core_node', ['road_id', 'position'])

        # Deleting model 'Alias'
        db.delete_table('core_alias')

        # Deleting model 'Road'
        db.delete_table('core_road')

        # Deleting model 'Node'
        db.delete_table('core_node')

        # Deleting model 'Section'
        db.delete_table('core_section')

        # Deleting model 'Situation'
        db.delete_table('core_situation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.alias': {
            'Meta': {'object_name': 'Alias'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'alias'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.node': {
            'Meta': {'ordering': "['road', 'position']", 'unique_together': "(('road', 'position'),)", 'object_name': 'Node'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {}),
            'road': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Road']"})
        },
        'core.road': {
            'Meta': {'object_name': 'Road'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'core.section': {
            'Meta': {'ordering': "['road', 'position']", 'unique_together': "(('road', 'direction', 'position'), ('road', 'direction', 'start'), ('road', 'direction', 'end'))", 'object_name': 'Section'},
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'end': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'end_section'", 'to': "orm['core.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'road': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Road']"}),
            'start': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'start_section'", 'to': "orm['core.Node']"})
        },
        'core.situation': {
            'Meta': {'object_name': 'Situation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_from_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rating': ('django.db.models.fields.SmallIntegerField', [], {}),
            'reason': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']"}),
            'status_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
