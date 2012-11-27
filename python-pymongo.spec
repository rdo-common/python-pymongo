%if 0%{?fedora} > 17
%global with_python3 1
%else
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%endif

# Fix private-shared-object-provides error
%{?filter_setup:
%filter_provides_in %{python_sitearch}.*\.so$
%filter_setup
}

Name:           python-pymongo
Version:        2.3
Release:        4%{?dist}
Summary:        Python driver for MongoDB

Group:          Development/Languages
# All code is ASL 2.0 except bson/time64*.{c,h} which is MIT
License:        ASL 2.0 and MIT
URL:            http://api.mongodb.org/python
Source0:        http://pypi.python.org/packages/source/p/pymongo/pymongo-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:       python-bson = %{version}-%{release}

Provides:       pymongo = %{version}-%{release}
Obsoletes:      pymongo <= 2.1.1-3

BuildRequires:  python2-devel
BuildRequires:  python-nose
BuildRequires:  python-setuptools

%if 0%{?with_python3}
BuildRequires:  python-tools
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif # if with_python3

# Mongodb must run on a little-endian CPU (see bug #630898)
ExcludeArch:    ppc ppc64 %{sparc} s390 s390x

%description
The Python driver for MongoDB.

%if 0%{?with_python3}
%package -n python3-pymongo
Summary:        Python driver for MongoDB
Group:          Development/Languages
Requires:       python3-bson = %{version}-%{release}

%description -n python3-pymongo
The Python driver for MongoDB.  This package contains the python3 version of
this module.
%endif # with_python3

%package python-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       pymongo-gridfs = %{version}-%{release}
Obsoletes:      pymongo-gridfs <= 2.1.1-3

%description python-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.

%if 0%{?with_python3}
%package -n python3-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.  This package
contains the python3 version of this module.
%endif # with_python3

%package -n python-bson
Summary:        Python bson library
Group:          Development/Libraries

%description -n python-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.

%if 0%{?with_python3}
%package -n python3-bson
Summary:        Python bson library
Group:          Development/Libraries

%description -n python3-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.  This package
contains the python3 version of this module.
%endif # with_python3

%prep
%setup -q -n pymongo-%{version}
rm -r pymongo.egg-info

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
2to3 --write --nobackups --no-diffs %{py3dir}
%endif # with_python3

%build
CFLAGS="%{optflags}" %{__python} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
CFLAGS="%{optflags}" %{__python3} setup.py build
popd
%endif # with_python3

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
popd
%endif # with_python3

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python_sitearch}/pymongo
%{python_sitearch}/pymongo-%{version}-*.egg-info

%if 0%{?with_python3}
%files -n python3-pymongo
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python3_sitearch}/pymongo
%{python3_sitearch}/pymongo-%{version}-*.egg-info
%endif # with_python3

%files python-pymongo-gridfs
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python_sitearch}/gridfs

%if 0%{?with_python3}
%files -n python3-pymongo-gridfs
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python3_sitearch}/gridfs
%endif # with_python3

%files -n python-bson
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python_sitearch}/bson

%if 0%{?with_python3}
%files -n python3-bson
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO README.rst doc
%{python3_sitearch}/bson
%endif # with_python3

%check
# Exclude tests that require an active MongoDB connection
 exclude='(^test_binary$'
exclude+='|^test_collection$'
exclude+='|^test_common$'
exclude+='|^test_connection$'
exclude+='|^test_cursor$'
exclude+='|^test_database$'
exclude+='|^test_grid_file$'
exclude+='|^test_gridfs$'
exclude+='|^test_json_util$'
exclude+='|^test_master_slave_connection$'
exclude+='|^test_pooling$'
exclude+='|^test_pooling_gevent$'
exclude+='|^test_pymongo$'
exclude+='|^test_read_preferences$'
exclude+='|^test_replica_set_connection$'
exclude+='|^test_son_manipulator$'
exclude+='|^test_threads$'
exclude+='|^test_threads_replica_set_connection$'
exclude+=')'
pushd test
truncate --size=0 __init__.py
nosetests --exclude="$exclude"
popd

%changelog
* Tue Nov 27 2012 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-4
- Fix obsoletes for python-pymongo-gridfs subpackage

* Tue Nov 27 2012 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-3
- Fix requires to include the arch, and add docs to all subpackages

* Tue Nov 27 2012 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-2
- Remove preexisting egg-info

* Mon Nov 26 2012 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-1
- Rename, update to 2.3, and add support for Python 3

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 10 2012 Silas Sewell <silas@sewell.org> - 2.1.1-1
- Update to 2.1.1

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Jul 24 2011 Silas Sewell <silas@sewell.org> - 1.11-1
- Update to 1.11

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Nov 18 2010 Dan Horák <dan[at]danny.cz> - 1.9-5
- add ExcludeArch to match mongodb package

* Tue Oct 26 2010 Silas Sewell <silas@sewell.ch> - 1.9-4
- Add comment about multi-license

* Thu Oct 21 2010 Silas Sewell <silas@sewell.ch> - 1.9-3
- Fixed tests so they actually run
- Change python-devel to python2-devel

* Wed Oct 20 2010 Silas Sewell <silas@sewell.ch> - 1.9-2
- Add check section
- Use correct .so filter
- Added python3 stuff (although disabled)

* Tue Sep 28 2010 Silas Sewell <silas@sewell.ch> - 1.9-1
- Update to 1.9

* Tue Sep 28 2010 Silas Sewell <silas@sewell.ch> - 1.8.1-1
- Update to 1.8.1

* Sat Dec 05 2009 Silas Sewell <silas@sewell.ch> - 1.1.2-1
- Initial build
