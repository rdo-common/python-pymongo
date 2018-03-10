# Fix private-shared-object-provides error
%{?filter_setup:
%filter_provides_in %{python_sitearch}.*\.so$
%filter_setup
}

Name:           python-pymongo
Version:        3.6.1
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

%ifnarch armv7hl ppc64 s390 s390x
# These are needed for tests, and the tests don't work on armv7hl.
# MongoDB server is not available on big endian arches (ppc64, s390(x)).
BuildRequires:  mongodb-server
BuildRequires:  net-tools
BuildRequires:  procps-ng
%endif
BuildRequires:  python2-tools
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
BuildRequires:  python2-sphinx
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools


%description
The Python driver for MongoDB.


%package doc
BuildArch: noarch
Summary:   Documentation for python-pymongo


%description doc
Documentation for python-pymongo.


%package -n python2-bson
Summary:        Python bson library
%{?python_provide:%python_provide python2-bson}


%description -n python2-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.


%package -n python3-bson
Summary:        Python bson library
%{?python_provide:%python_provide python3-bson}


%description -n python3-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.  This package
contains the python3 version of this module.


%package -n python2-pymongo
Summary:        Python driver for MongoDB

Requires:       python2-bson%{?_isa} = %{version}-%{release}
Provides:       pymongo = %{version}-%{release}
Obsoletes:      pymongo <= 2.1.1-4
%{?python_provide:%python_provide python2-pymongo}


%description -n python2-pymongo
The Python driver for MongoDB.  This package contains the python2 version of
this module.


%package -n python3-pymongo
Summary:        Python driver for MongoDB
Requires:       python3-bson%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo}


%description -n python3-pymongo
The Python driver for MongoDB.  This package contains the python3 version of
this module.


%package -n python2-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Requires:       python2-pymongo%{?_isa} = %{version}-%{release}
Provides:       pymongo-gridfs = %{version}-%{release}
Obsoletes:      pymongo-gridfs <= 2.1.1-4
%{?python_provide:%python_provide python2-pymongo-gridfs}


%description -n python2-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.


%package -n python3-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Requires:       python3-pymongo%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo-gridfs}


%description -n python3-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.  This package
contains the python3 version of this module.


%prep
%setup -q -n mongo-python-driver-%{version}
%patch01 -p1 -b .ssl

# Remove the bundled ssl.match_hostname library as it was vulnerable to CVE-2013-7440
# and CVE-2013-2099, and isn't needed anyway since Fedora >= 22 has the needed module in the Python
# standard library.
rm pymongo/ssl_match_hostname.py

rm -rf %{py3dir}
cp -a . %{py3dir}


%build
%py2_build

pushd %{py3dir}
%py3_build
popd

pushd doc
make %{?_smp_mflags} html
popd


%install
%py2_install
# Fix permissions
chmod 755 %{buildroot}%{python2_sitearch}/bson/*.so
chmod 755 %{buildroot}%{python2_sitearch}/pymongo/*.so

pushd %{py3dir}
%py3_install
# Fix permissions
chmod 755 %{buildroot}%{python3_sitearch}/bson/*.so
chmod 755 %{buildroot}%{python3_sitearch}/pymongo/*.so
popd


%check
# For some reason, the tests never think they can connect to mongod on armv7hl even though netstat
# says it's listening. mongod is not available on big endian arches (ppc64, s390(x)).
%ifnarch armv7hl ppc64 s390 s390x

if [ "$(netstat -ln | grep 27017)" != "" ]
then
    pkill mongod
fi

mkdir ./mongod
mongod --fork --dbpath ./mongod --logpath ./mongod/mongod.log
# Give MongoDB some time to settle
while [ "$(netstat -ln | grep 27017)" == "" ]
do
    sleep 1
done

python2 setup.py test || (pkill mongod && exit 1)

pushd %{py3dir}
python3 setup.py test || (pkill mongod && exit 1)
popd

pkill mongod
%endif


%files doc
%license LICENSE
%doc doc/_build/html/*


%files -n python2-bson
%license LICENSE
%doc README.rst
%{python2_sitearch}/bson


%files -n python3-bson
%license LICENSE
%doc README.rst
%{python3_sitearch}/bson


%files -n python2-pymongo
%license LICENSE
%doc README.rst
%{python2_sitearch}/pymongo
%{python2_sitearch}/pymongo-%{version}-*.egg-info


%files -n python3-pymongo
%license LICENSE
%doc README.rst
%{python3_sitearch}/pymongo
%{python3_sitearch}/pymongo-%{version}-*.egg-info


%files -n python2-pymongo-gridfs
%license LICENSE
%doc README.rst
%{python2_sitearch}/gridfs


%files -n python3-pymongo-gridfs
%license LICENSE
%doc README.rst
%{python3_sitearch}/gridfs


%changelog
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

* Tue Dec 20 2016 Miro Hrončok <mhroncok@redhat.com> - 3.4.0-2
- Rebuild for Python 3.6

* Sun Dec 18 2016 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.4.0-1
- Update to 3.4.0 (#1400227).
- Use new install macros.
- Drop unneeded BuildRequires on python-nose.
- pymongo now requires bson by arch as it should.

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 3.3.0-6
- Rebuild for Python 3.6

* Tue Nov 29 2016 Dan Horák <dan[at]danny.cz> - 3.3.0-5
- Update test BRs

* Fri Nov 25 2016 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.3.0-4
- Run the tests with setup.py test instead of with nosetests.

* Fri Nov 25 2016 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.3.0-3
- Run the tests against a live mongod.

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.0-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Jul 15 2016 Randy Barlow <bowlofeggs@fedoraproject.org> - 3.3.0-1
- Update to 3.3.0 (#1356334).
- Remove the exclude arch on big endian systems, since 3.3.0 now supports them.
- Use the newer Python build macros.
- Add a skip test on another test that requires a running mongod.
- Convert the -doc subpackage into a noarch, as it should be.
- python2-pymongo-gridfs now requires python2-pymongo(isa) instead of python-pymongo(isa).
- Build the docs in parallel.

* Tue Mar 15 2016 Randy Barlow <rbarlow@redhat.com> - 3.2.2-1
- Update to 3.2.2 (#1318073).

* Wed Feb 03 2016 Randy Barlow <rbarlow@redhat.com> - 3.2.1-1
- Remove use of needless defattr macros (#1303426).
- Update to 3.2.1 (#1304137).
- Remove lots of if statements as this spec file will only be used on Rawhide.
- Remove dependency on python-backports-ssl_match_hostname as it is not needed in Fedora.
- Rework the patch for CVE-2013-7440 and CVE-2013-2099 so that it exclusively uses code from Python.

* Tue Jan 19 2016 Randy Barlow <rbarlow@redhat.com> - 3.2-1
- Update to 3.2.
- Rename the python- subpackages with a python2- prefix.
- Add a -doc subpackage with built html docs.
- Skip a few new tests that use MongoDB.
- Reorganize the spec file a bit.
- Use the license macro.
- Pull source from GitHub.

* Mon Jan 18 2016 Randy Barlow <rbarlow@redhat.com> - 3.0.3-3
- Do not use 2to3 for Python 3 (#1294130).

* Wed Nov 04 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.0.3-2
- Rebuilt for Python 3.5

* Thu Oct 01 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 3.0.3-1
- Upstream 3.0.3
- Fix CVE-2013-7440 (RHBZ#1231231 #1231232)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.5.2-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jun 13 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5.2-2
- Bump the obsoletes version for pymongo-gridfs

* Wed Jun 12 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5.2-1
- Update to pymongo 2.5.2

* Tue Jun 11 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5-5
- Bump the obsoletes version

* Wed Apr 24 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5-4
- Fix the test running procedure

* Wed Apr 24 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5-3
- Exclude tests in pymongo 2.5 that depend on MongoDB

* Mon Apr 22 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.5-1
- Update to PyMongo 2.5 (bug #954152)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jan  5 2013 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-6
- Fix dependency of python3-pymongo-gridfs (bug #892214)

* Tue Nov 27 2012 Andrew McNabb <amcnabb@mcnabbs.org> - 2.3-5
- Fix the name of the python-pymongo-gridfs subpackage

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
