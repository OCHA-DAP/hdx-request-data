import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.hdx_request_data.logic import validators


class Hdx_Request_DataPlugin(plugins.SingletonPlugin,
                             toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'hdx_request_data')

    # IDatasetForm

    def _modify_package_schema(self, schema, type='create'):
        hdx_package_schema = {}
        requestdata_schema = {}

        convert_to_extras = toolkit.get_converter('convert_to_extras')
        ignore_missing = toolkit.get_validator('ignore_missing')
        not_empty = toolkit.get_validator('not_empty')

        for plugin in plugins.PluginImplementations(plugins.IDatasetForm):
            if plugin.name == 'hdx_package':
                if type == 'create':
                    hdx_package_schema = plugin.create_package_schema()
                elif type == 'update':
                    hdx_package_schema = plugin.update_package_schema()
            elif plugin.name == 'requestdata':
                if type == 'create':
                    requestdata_schema = plugin.create_package_schema()
                elif type == 'update':
                    requestdata_schema = plugin.update_package_schema()

        schema.update(requestdata_schema)
        schema.update(hdx_package_schema)

        schema.update({
            'methodology': [ignore_missing, convert_to_extras],
            'data_update_frequency': [ignore_missing, convert_to_extras],
            'field_names': [not_empty, convert_to_extras],
            'file_types': [not_empty, convert_to_extras],
            'num_of_rows': [ignore_missing, validators.is_positive_integer,
                            convert_to_extras]
        })

        schema.pop('license_id')
        schema.pop('license_other')

        return schema

    def create_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema, type='create')

        return schema

    def update_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema, type='update')

        return schema

    def show_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).show_package_schema()

        hdx_package_schema = {}
        requestdata_schema = {}

        convert_from_extras = toolkit.get_converter('convert_from_extras')
        ignore_missing = toolkit.get_validator('ignore_missing')
        not_empty = toolkit.get_validator('not_empty')

        for plugin in plugins.PluginImplementations(plugins.IDatasetForm):
            if plugin.name == 'hdx_package':
                hdx_package_schema = plugin.show_package_schema()
            elif plugin.name == 'requestdata':
                requestdata_schema = plugin.show_package_schema()

        schema.update(requestdata_schema)
        schema.update(hdx_package_schema)

        schema.update({
            'methodology': [convert_from_extras, ignore_missing],
            'data_update_frequency': [convert_from_extras, ignore_missing],
            'field_names': [convert_from_extras, not_empty],
            'file_types': [convert_from_extras, not_empty],
            'num_of_rows': [convert_from_extras, ignore_missing,
                            validators.is_positive_integer]
        })

        return schema

    def is_fallback(self):
        return False

    def package_types(self):
        return ['hdx-requestdata-metadata-only']
