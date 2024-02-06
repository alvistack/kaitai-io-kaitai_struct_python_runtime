# Copyright 2025 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

Name: python-kaitaistruct
Epoch: 100
Version: 0.10
Release: 1%{?dist}
BuildArch: noarch
Summary: Kaitai Struct: runtime for Python
License: MIT
URL: https://github.com/kaitai-io/kaitai_struct_python_runtime/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-wheel

%description
Kaitai Struct is a declarative language used for describe various binary
data structures, laid out in files or in memory: i.e. binary file
formats, network stream packet formats, etc.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%py3_build

%install
%py3_install
find %{buildroot}%{python3_sitelib} -type f -name '*.pyc' -exec rm -rf {} \;
fdupes -qnrps %{buildroot}%{python3_sitelib}

%check

%if 0%{?suse_version} > 1500
%package -n python%{python3_version_nodots}-kaitaistruct
Summary: Kaitai Struct: runtime for Python
Requires: python3
Provides: python3-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python3dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(kaitaistruct) = %{epoch}:%{version}-%{release}

%description -n python%{python3_version_nodots}-kaitaistruct
Kaitai Struct is a declarative language used for describe various binary
data structures, laid out in files or in memory: i.e. binary file
formats, network stream packet formats, etc.

%files -n python%{python3_version_nodots}-kaitaistruct
%license LICENSE
%{python3_sitelib}/*
%endif

%if 0%{?sle_version} > 150000
%package -n python3-kaitaistruct
Summary: Kaitai Struct: runtime for Python
Requires: python3
Provides: python3-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python3dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(kaitaistruct) = %{epoch}:%{version}-%{release}

%description -n python3-kaitaistruct
Kaitai Struct is a declarative language used for describe various binary
data structures, laid out in files or in memory: i.e. binary file
formats, network stream packet formats, etc.

%files -n python3-kaitaistruct
%license LICENSE
%{python3_sitelib}/*
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package -n python3-kaitaistruct
Summary: Kaitai Struct: runtime for Python
Requires: python3
Provides: python3-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python3dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(kaitaistruct) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-kaitaistruct = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(kaitaistruct) = %{epoch}:%{version}-%{release}

%description -n python3-kaitaistruct
Kaitai Struct is a declarative language used for describe various binary
data structures, laid out in files or in memory: i.e. binary file
formats, network stream packet formats, etc.

%files -n python3-kaitaistruct
%license LICENSE
%{python3_sitelib}/*
%endif

%changelog