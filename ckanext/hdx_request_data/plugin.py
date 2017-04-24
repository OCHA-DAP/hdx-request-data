import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


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

    def _modify_package_schema(self, schema):
        hdx_package_schema = {}
        requestdata_schema = {}

        convert_to_extras = toolkit.get_converter('convert_to_extras')
        ignore_missing = toolkit.get_validator('ignore_missing')
        not_empty = toolkit.get_validator('not_empty')
        int_validator = toolkit.get_validator('int_validator')

        for plugin in plugins.PluginImplementations(plugins.IDatasetForm):
            if plugin.name == 'hdx_package':
                hdx_package_schema = plugin.create_package_schema()
            elif plugin.name == 'requestdata':
                requestdata_schema = plugin.create_package_schema()

        schema.update(hdx_package_schema)
        schema.update(requestdata_schema)

        schema.update({
            'methodology': [ignore_missing, convert_to_extras],
            'data_update_frequency': [ignore_missing, convert_to_extras],
            'field_names': [not_empty, convert_to_extras],
            'file_types': [not_empty, convert_to_extras],
            'num_of_rows': [ignore_missing, int_validator]
        })

        schema.pop('license_id')
        schema.pop('license_other')

        # "groups_list" is temporary removed from the schema because there are
        # some issues when creating/updating a package
        schema.pop('groups_list')

        return schema

    def create_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def update_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def show_package_schema(self):
        schema = super(Hdx_Request_DataPlugin, self).show_package_schema()

        return schema

    def is_fallback(self):
        return False

    def package_types(self):
        return ['hdx-requestdata-metadata-only']

    def validate(self, context, data_dict, schema, action):
        if action in ['package_create', 'package_update']:
            tags = data_dict.get('tags')

            if not tags:
                raise toolkit.ValidationError('Missing value: tags')

        return toolkit.navl_validate(data_dict, schema, context)
