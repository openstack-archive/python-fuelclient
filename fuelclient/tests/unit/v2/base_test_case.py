from argparse import Namespace

from oslotest import base as oslo_base


class BaseTestCase(oslo_base.BaseTestCase):

    def create_namespace(self, columns=[], env=None, formatter='table',
                         group=None, labels=None, max_width=0, noindent=False,
                         online=None, quote_mode='nonnumeric', role=None,
                         sort_columns=['id'], status=None):
        return Namespace(
            columns=columns, env=env, formatter=formatter, group=group,
            labels=labels, max_width=max_width, noindent=noindent,
            online=online, quote_mode=quote_mode, role=role,
            sort_columns=sort_columns, status=status)
