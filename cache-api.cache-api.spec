Name:           cache-api
Version:        1.0.1
Release:        1%{?dist}
Summary:        Cache API service with Redis backend

License:        MIT
URL:            https://github.com/cache-api
Source0:        cache-api-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3 python3-flask python3-redis python3-requests python3-PyYAML redis

%description
Cache API service that provides caching layer using Redis with Flask backend.

%prep
%autosetup -n cache-api-%{version}

%build
# Nothing to build for Python script

%install
# Create directories
install -d %{buildroot}%{_bindir}
install -d %{buildroot}/opt/cache-api
install -d %{buildroot}%{_sysconfdir}/cache-api
install -d %{buildroot}%{_sysconfdir}/systemd/system
install -d %{buildroot}%{_var}/log/cache-api

# Install main application
install -m 755 cache-api.py %{buildroot}/opt/cache-api/

# Install configuration
install -m 644 %{_sourcedir}/config.yaml %{buildroot}%{_sysconfdir}/cache-api/

# Install systemd service
install -m 644 %{_sourcedir}/cache-api.service %{buildroot}%{_sysconfdir}/systemd/system/

# Create log directory
install -d %{buildroot}%{_localstatedir}/log/cache-api

%pre
getent group cacheapi >/dev/null || groupadd -r cacheapi
getent passwd cacheapi >/dev/null || useradd -r -g cacheapi -d /opt/cache-api -s /sbin/nologin -c "Cache API user" cacheapi

%post
# Set permissions
chown -R cacheapi:cacheapi /opt/cache-api
chown -R cacheapi:cacheapi %{_sysconfdir}/cache-api
chown -R cacheapi:cacheapi %{_var}/log/cache-api

# Reload systemd and enable service
systemctl daemon-reload >/dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ]; then
    # Package is being removed, not upgraded
    systemctl --no-reload disable cache-api.service >/dev/null 2>&1 || :
    systemctl stop cache-api.service >/dev/null 2>&1 || :
fi

%postun
if [ $1 -ge 1 ]; then
    # Package upgrade, not uninstall
    systemctl try-restart cache-api.service >/dev/null 2>&1 || :
fi

%files
%attr(755, cacheapi, cacheapi) /opt/cache-api/cache-api.py
%config(noreplace) %{_sysconfdir}/cache-api/config.yaml
%{_sysconfdir}/systemd/system/cache-api.service
%dir %attr(755, cacheapi, cacheapi) %{_sysconfdir}/cache-api
%dir %attr(755, cacheapi, cacheapi) /opt/cache-api
%dir %attr(755, cacheapi, cacheapi) %{_var}/log/cache-api
