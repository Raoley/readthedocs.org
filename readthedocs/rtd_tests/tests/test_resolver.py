from django.test import TestCase
from django.test.utils import override_settings

from readthedocs.projects.models import Project, Domain
from readthedocs.rtd_tests.utils import create_user
from readthedocs.core.resolver import (resolve_path, smart_resolve_path,
                                       smart_resolve, smart_resolve_domain)

from django_dynamic_fixture import get


class ResolverBase(TestCase):

    def setUp(self):
        self.owner = create_user(username='owner', password='test')
        self.tester = create_user(username='tester', password='test')
        self.pip = get(Project, slug='pip', users=[self.owner], main_language_project=None)
        self.subproject = get(Project, slug='sub', language='ja', users=[self.owner], main_language_project=None)
        self.translation = get(Project, slug='trans', language='ja', users=[self.owner], main_language_project=None)
        self.pip.add_subproject(self.subproject)
        self.pip.translations.add(self.translation)


class SmartResolverPathTests(ResolverBase):

    def test_smart_resolver_filename(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='/foo/bar/blah.html')
            self.assertEqual(url, '/docs/pip/en/latest/foo/bar/blah.html')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='/foo/bar/blah.html')
            self.assertEqual(url, '/en/latest/foo/bar/blah.html')

        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='foo/bar/blah.html')
            self.assertEqual(url, '/docs/pip/en/latest/foo/bar/blah.html')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='foo/bar/blah.html')
            self.assertEqual(url, '/en/latest/foo/bar/blah.html')

        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='')
            self.assertEqual(url, '/docs/pip/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='')
            self.assertEqual(url, '/en/latest/')

    def test_smart_resolver_subdomain(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='index.html')
            self.assertEqual(url, '/docs/pip/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='index.html')
            self.assertEqual(url, '/en/latest/')

    def test_smart_resolver_domain_object(self):
        self.domain = get(Domain, url='http://docs.foobar.com', project=self.pip, canonical=True)
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='index.html')
            self.assertEqual(url, '/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='index.html')
            self.assertEqual(url, '/en/latest/')

    def test_smart_resolver_domain_object_not_canonical(self):
        self.domain = get(Domain, url='http://docs.foobar.com', project=self.pip, canonical=False)
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.pip, filename='')
            self.assertEqual(url, '/docs/pip/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.pip, filename='')
            self.assertEqual(url, '/en/latest/')

    def test_smart_resolver_subproject_subdomain(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/docs/pip/projects/sub/ja/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/projects/sub/ja/latest/')

    def test_smart_resolver_subproject_single_version(self):
        self.subproject.single_version = True
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/docs/pip/projects/sub/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/projects/sub/')

    def test_smart_resolver_subproject_both_single_version(self):
        self.pip.single_version = True
        self.subproject.single_version = True
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/docs/pip/projects/sub/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.subproject, filename='index.html')
            self.assertEqual(url, '/projects/sub/')

    def test_smart_resolver_translation(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_path(project=self.translation, filename='index.html')
            self.assertEqual(url, '/docs/pip/ja/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_path(project=self.translation, filename='index.html')
            self.assertEqual(url, '/ja/latest/')


class ResolverPathTests(ResolverBase):

    def test_resolver_force_single_version(self):
        self.pip.single_version = False
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', single_version=True)
            self.assertEqual(url, '/docs/pip/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', single_version=True)
            self.assertEqual(url, '/')

    def test_resolver_force_domain(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', cname=True)
            self.assertEqual(url, '/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', cname=True)
            self.assertEqual(url, '/en/latest/')

    def test_resolver_force_domain_single_version(self):
        self.pip.single_version = False
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', single_version=True, cname=True)
            self.assertEqual(url, '/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', single_version=True, cname=True)
            self.assertEqual(url, '/')

    def test_resolver_force_language(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', language='cz')
            self.assertEqual(url, '/docs/pip/cz/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', language='cz')
            self.assertEqual(url, '/cz/latest/')

    def test_resolver_force_version(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', version_slug='foo')
            self.assertEqual(url, '/docs/pip/en/foo/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', version_slug='foo')
            self.assertEqual(url, '/en/foo/')

    def test_resolver_force_language_version(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.pip, filename='index.html', language='cz', version_slug='foo')
            self.assertEqual(url, '/docs/pip/cz/foo/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.pip, filename='index.html', language='cz', version_slug='foo')
            self.assertEqual(url, '/cz/foo/')

    def test_resolver_no_force_translation(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.translation, filename='index.html', language='cz')
            self.assertEqual(url, '/docs/pip/ja/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.translation, filename='index.html', language='cz')
            self.assertEqual(url, '/ja/latest/')

    def test_resolver_no_force_translation_with_version(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = resolve_path(project=self.translation, filename='index.html', language='cz', version_slug='foo')
            self.assertEqual(url, '/docs/pip/ja/foo/')
        with override_settings(USE_SUBDOMAIN=True):
            url = resolve_path(project=self.translation, filename='index.html', language='cz', version_slug='foo')
            self.assertEqual(url, '/ja/foo/')


class ResolverDomainTests(ResolverBase):

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_domain_resolver(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_domain(project=self.pip)
            self.assertEqual(url, 'readthedocs.org')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_domain(project=self.pip)
            self.assertEqual(url, 'pip.readthedocs.org')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_domain_resolver_with_domain_object(self):
        self.domain = get(Domain, url='http://docs.foobar.com', project=self.pip, canonical=True)
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_domain(project=self.pip)
            self.assertEqual(url, 'docs.foobar.com')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_domain(project=self.pip)
            self.assertEqual(url, 'docs.foobar.com')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_domain_resolver_subproject(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_domain(project=self.subproject)
            self.assertEqual(url, 'readthedocs.org')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_domain(project=self.subproject)
            self.assertEqual(url, 'pip.readthedocs.org')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_domain_resolver_translation(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve_domain(project=self.translation)
            self.assertEqual(url, 'readthedocs.org')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve_domain(project=self.translation)
            self.assertEqual(url, 'pip.readthedocs.org')


class ResolverTests(ResolverBase):

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_resolver(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://readthedocs.org/docs/pip/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://pip.readthedocs.org/en/latest/')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_resolver_domain(self):
        self.domain = get(Domain, url='http://docs.foobar.com', project=self.pip, canonical=True)
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://docs.foobar.com/en/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://docs.foobar.com/en/latest/')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_resolver_subproject(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve(project=self.subproject)
            self.assertEqual(url, 'http://readthedocs.org/docs/pip/projects/sub/ja/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve(project=self.subproject)
            self.assertEqual(url, 'http://pip.readthedocs.org/projects/sub/ja/latest/')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_resolver_translation(self):
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve(project=self.translation)
            self.assertEqual(url, 'http://readthedocs.org/docs/pip/ja/latest/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve(project=self.translation)
            self.assertEqual(url, 'http://pip.readthedocs.org/ja/latest/')

    @override_settings(PRODUCTION_DOMAIN='readthedocs.org')
    def test_resolver_single_version(self):
        self.pip.single_version = True
        with override_settings(USE_SUBDOMAIN=False):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://readthedocs.org/docs/pip/')
        with override_settings(USE_SUBDOMAIN=True):
            url = smart_resolve(project=self.pip)
            self.assertEqual(url, 'http://pip.readthedocs.org/')
