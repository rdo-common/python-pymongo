# Fix private-shared-object-provides error
%{?filter_setup:
%filter_provides_in %{python_sitearch}.*\.so$
%filter_setup
}

%global bootstrap 0
%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_with python2
%bcond_without python3
%else
%bcond_without python2
%bcond_with python3
%endif

Name:           python-pymongo
Version:        3.7.2
Release:        1%{?dist}

# All code is ASL 2.0 except bson/time64*.{c,h} which is MIT
License:        ASL 2.0 and MIT
Summary:        Python driver for MongoDB
URL:            http://api.mongodb.org/python
Source0:        https://github.com/mongodb/mongo-python-driver/archive/%{version}/pymongo-%{version}.tar.gz
# This patch removes the bundled ssl.match_hostname library as it was vulnerable to CVE-2013-7440
# and CVE-2013-2099, and wasn't needed anyway since Fedora >= 22 has the needed module in the Python
# standard library. It also adjusts imports so that they exclusively use the code from Python.
Patch01:        0001-Use-ssl.match_hostname-from-the-Python-stdlib.patch

BuildRequires:  gcc
%ifnarch armv7hl ppc64 s390 s390x
# These are needed for tests, and the tests don't work on armv7hl.
# MongoDB server is not available on big endian arches (ppc64, s390(x)).
%if 0%{!?bootstrap:1}
BuildRequires:  mongodb-server
%if %{with python3}
BuildRequires:  python3-sphinx
%endif
%endif
BuildRequires:  net-tools
BuildRequires:  procps-ng
%endif
%if %{with python3}
BuildRequires:  python3-tools
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif
%if %{with python2}
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
%endif


%description
The Python driver for MongoDB.


%package doc
BuildArch: noarch
Summary:   Documentation for python-pymongo


%description doc
Documentation for python-pymongo.


%if %{with python2}
%package -n python2-bson
Summary:        Python bson library
%{?python_provide:%python_provide python2-bson}


%description -n python2-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.
%endif


%if %{with python3}
%package -n python3-bson
Summary:        Python bson library
%{?python_provide:%python_provide python3-bson}


%description -n python3-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.  This package
contains the python3 version of this module.
%endif


%if %{with python2}
%package -n python2-pymongo
Summary:        Python driver for MongoDB

Requires:       python2-bson%{?_isa} = %{version}-%{release}
Provides:       pymongo = %{version}-%{release}
Obsoletes:      pymongo <= 2.1.1-4
%{?python_provide:%python_provide python2-pymongo}


%description -n python2-pymongo
The Python driver for MongoDB.  This package contains the python2 version of
this module.
%endif


%if %{with python3}
%package -n python3-pymongo
Summary:        Python driver for MongoDB
Requires:       python3-bson%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo}


%description -n python3-pymongo
The Python driver for MongoDB.  This package contains the python3 version of
this module.
%endif


%if %{with python2}
%package -n python2-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Requires:       python2-pymongo%{?_isa} = %{version}-%{release}
Provides:       pymongo-gridfs = %{version}-%{release}
Obsoletes:      pymongo-gridfs <= 2.1.1-4
%{?python_provide:%python_provide python2-pymongo-gridfs}


%description -n python2-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.
%endif


%if %{with python3}
%package -n python3-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Requires:       python3-pymongo%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo-gridfs}


%description -n python3-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.  This package
contains the python3 version of this module.
%endif


%prep
%setup -q -n mongo-python-driver-%{version}
%patch01 -p1 -b .ssl

# Remove the bundled ssl.match_hostname library as it was vulnerable to CVE-2013-7440
# and CVE-2013-2099, and isn't needed anyway since Fedora >= 22 has the needed module in the Python
# standard library.
rm pymongo/ssl_match_hostname.py

%if %{with python2} && %{with python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif


%build
%if %{with python2}
%py2_build
%endif

%if %{with python2} && %{with python3}
pushd %{py3dir}
%endif
%if %{with python3}
%py3_build
%endif
%if %{with python2} && %{with python3}
popd
%endif

%if 0%{!?bootstrap:1}
pushd doc
make %{?_smp_mflags} html
popd
%endif


%install
%if %{with python2}
%py2_install
# Fix permissions
chmod 755 %{buildroot}%{python2_sitearch}/bson/*.so
chmod 755 %{buildroot}%{python2_sitearch}/pymongo/*.so
%endif

%if %{with python2} && %{with python3}
pushd %{py3dir}
%endif
%if %{with python3}
%py3_install
# Fix permissions
chmod 755 %{buildroot}%{python3_sitearch}/bson/*.so
chmod 755 %{buildroot}%{python3_sitearch}/pymongo/*.so
%endif
%if %{with python2} && %{with python3}
popd
%endif


%check
# For some reason, the tests never think they can connect to mongod on armv7hl even though netstat
# says it's listening. mongod is not available on big endian arches (ppc64, s390(x)).
%ifnarch armv7hl ppc64 s390 s390x
%if 0%{!?bootstrap:1}

if [ "$(netstat -ln | grep :27017)" != "" ]
then
    pkill mongod
fi

mkdir ./mongod
mongod --fork --dbpath ./mongod --logpath ./mongod/mongod.log
# Give MongoDB some time to settle
while [ "$(netstat -ln | grep :27017)" == "" ]
do
    sleep 1
done

%if %{with python2}
python2 setup.py test || (pkill mongod && exit 1)
%endif

%if %{with python2} && %{with python3}
pushd %{py3dir}
%endif
%if %{with python3}
python3 setup.py test || (pkill mongod && exit 1)
%endif
%if %{with python2} && %{with python3}
popd
%endif

pkill mongod
%endif
%endif


%files doc
%license LICENSE
%if 0%{!?bootstrap:1}
%doc doc/_build/html/*
%endif


%if %{with python2}
%files -n python2-bson
%license LICENSE
%doc README.rst
%{python2_sitearch}/bson
%endif


%if %{with python3}
%files -n python3-bson
%license LICENSE
%doc README.rst
%{python3_sitearch}/bson
%endif


%if %{with python2}
%files -n python2-pymongo
%license LICENSE
%doc README.rst
%{python2_sitearch}/pymongo
%{python2_sitearch}/pymongo-%{version}-*.egg-info
%endif


%if %{with python3}
%files -n python3-pymongo
%license LICENSE
%doc README.rst
%{python3_sitearch}/pymongo
%{python3_sitearch}/pymongo-%{version}-*.egg-info
%endif


%if %{with python2}
%files -n python2-pymongo-gridfs
%license LICENSE
%doc README.rst
%{python2_sitearch}/gridfs
%endif


%if %{with python3}
%files -n python3-pymongo-gridfs
%license LICENSE
%doc README.rst
%{python3_sitearch}/gridfs
%endif


%changelog
* Thu Feb 28 2019 Yatin Karel <ykarel@redhat.com> - 3.7.2-1
- Update to 3.7.2
- http://api.mongodb.com/python/3.7.2/changelog.html

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 28 2019 Miro Hrončok <mhroncok@redhat.com> - 3.7.1-3
- Subpackages python2-bson, python2-pymongo, python2-pymongo-gridfs have been removed
  See https://fedoraproject.org/wiki/Changes/Mass_Python_2_Package_Removal

* Mon Dec 10 2018 Honza Horak <hhorak@redhat.com> - 3.7.1-3
- Add bootstrap macro and python2 condition

* Tue Jul 31 2018 Florian Weimer <fweimer@redhat.com> - 3.7.1-2
- Rebuild with fixed binutils

* Mon Jul 30 2018 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.7.1-1
- Update to 3.7.1 (#1601651).
- http://api.mongodb.com/python/3.7.1/changelog.html

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 3.6.1-2
- Rebuilt for Python 3.7

* Sat Mar 10 2018 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.6.1-1
- Update to 3.6.1 (#1550757).
- http://api.mongodb.com/python/3.6.1/changelog.html

* Tue Feb 27 2018 Iryna Shcherbina <ishcherb@redhat.com> - 3.6.0-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Mon Feb 19 2018 Marek Skalický <mskalick@redhat.com> - 3.6.0-1
- Rebase to latest release

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Sep 22 2017 Marek Skalický <mskalick@redhat.com> - 3.5.1-1
- Update to latest version

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.4.0-5
- Rebuild due to bug in RPM (RHBZ #1468476)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 06 2017 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.4.0-3
- Run the test suite in the check section (#1409251).
