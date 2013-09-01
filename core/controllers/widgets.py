# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for interactive and non-interactive widgets."""

__author__ = 'sll@google.com (Sean Lip)'

import collections

import feconf
from core.controllers import base
from core.platform import models
user_services = models.Registry.import_user_services()
from core.domain import widget_domain
import utils


class WidgetRepositoryPage(base.BaseHandler):
    """Displays the widget repository page."""

    def get(self):
        """Returns the widget repository page."""
        if self.request.get('iframed') == 'true':
            self.values['iframed'] = True
        if self.request.get('interactive') == 'true':
            self.values['interactive'] = True
        if 'parent_index' in self.request.GET.keys():
            self.values['parent_index'] = self.request.get('parent_index')
        if user_services.is_current_user_admin(self.request):
            self.values['admin'] = True
        self.render_template('editor/widget_repository.html')


class WidgetRepositoryHandler(base.BaseHandler):
    """Populates the widget repository pages."""

    def get(self, widget_type):
        """Handles GET requests."""
        try:
            widget_list = widget_domain.Registry.get_widgets_of_type(
                widget_type)
        except Exception:
            raise self.PageNotFoundException

        widgets = collections.defaultdict(list)
        for widget in widget_list:
            widgets[widget.category].append(
                widget.get_widget_instance_dict({}, {}))

        for category in widgets:
            widgets[category].sort()

        response = {'widgets': widgets}

        if widget_type == feconf.NONINTERACTIVE_PREFIX:
            parent_index = self.request.get('parent_index')
            if parent_index is None:
                raise Exception(
                    'Non-interactive widgets require a parent_index.')
            else:
                response['parent_index'] = parent_index

        self.render_json(response)


class WidgetHandler(base.BaseHandler):
    """Returns instance dicts for individual widgets."""

    def post(self, widget_type, widget_id):
        """Handles POST requests for parameterized widgets."""
        # TODO(sll): Rename 'params' in the frontend.
        customization_args = self.payload.get('params', {})

        state_params_dict = {}
        state_params_given = self.payload.get('state_params')
        if state_params_given:
            for param in state_params_given:
                # Pick a random parameter for each key.
                state_params_dict[param['name']] = (
                    utils.get_random_choice(param['values']))

        widget = widget_domain.Registry.get_widget_by_id(
            widget_type, widget_id)
        widget_instance_dict = widget.get_widget_instance_dict(
            customization_args, state_params_dict, kvps_only=True)
        response = {'widget': widget_instance_dict}

        if widget_type == feconf.NONINTERACTIVE_PREFIX:
            parent_index = self.request.get('parent_index')
            if parent_index is None:
                raise Exception(
                    'Non-interactive widgets require a parent_index.')
            else:
                response['parent_index'] = parent_index

        self.render_json(response)
