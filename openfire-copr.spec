Summary: Openfire XMPP Server
Name: openfire
Version: 4.7.5
Release: 1%{?dist}
BuildRoot: %{_builddir}/%{name}-root
Source0: https://github.com/igniterealtime/Openfire/archive/refs/tags/v%{version}.tar.gz
%ifarch noarch
# Note that epoch is set here to 1, this appears to be consistent with non-Redhat
# jres as well due to an ancient problem with java-1.5.0-ibm jpackage RPM
Requires: java >= 1:11.0.0
%endif
Group: Applications/Communications
Vendor: Igniterealtime Community
License: Apache License 2.0
URL: https://igniterealtime.org/projects/openfire/

%define prefix /opt
%define homedir %{prefix}/openfire
# couldn't find another way to disable the brp-java-repack-jars which was called in __os_install_post
%define __os_install_post %{nil}
%define debug_package %{nil}

%description
Openfire is a leading Open Source, cross-platform IM server based on the
XMPP (Jabber) protocol. It has great performance, is easy to setup and use,
and delivers an innovative feature set.

%prep
%setup -q -n openfire_src

%build
cd build
ant openfire
ant -Dplugin=search plugin
cd ..

%install
# Prep the install location.
rm -rf %{_builddir}
mkdir -p %{_builddir}%{prefix}
# Copy over the main install tree.
cp -R target/openfire %{_builddir}%{homedir}
%ifnarch noarch
# Set up distributed JRE
pushd %{_builddir}%{homedir}
gzip -cd %{SOURCE0} | tar xvf -
popd
%endif
# Set up the init script.
mkdir -p %{_builddir}/etc/init.d
cp %{_builddir}%{homedir}/bin/extra/redhat/openfire %{_builddir}/etc/init.d/openfire
chmod 755 %{_builddir}/etc/init.d/openfire
# Make the startup script executable.
chmod 755 %{_builddir}%{homedir}/bin/openfire.sh
# Set up the sysconfig file.
mkdir -p %{_builddir}/etc/sysconfig
cp %{_builddir}%{homedir}/bin/extra/redhat/openfire-sysconfig %{_builddir}/etc/sysconfig/openfire
# Copy over the documentation
cp -R documentation %{_builddir}%{homedir}/documentation
cp changelog.html %{_builddir}%{homedir}/
cp LICENSE.html %{_builddir}%{homedir}/
cp README.html %{_builddir}%{homedir}/
# Copy over the i18n files
cp -R resources/i18n %{_builddir}%{homedir}/resources/i18n
# Make sure scripts are executable
chmod 755 %{_builddir}%{homedir}/bin/extra/openfired
chmod 755 %{_builddir}%{homedir}/bin/extra/redhat-postinstall.sh
# Move over the embedded db viewer pieces
mv %{_builddir}%{homedir}/bin/extra/embedded-db.rc %{_builddir}%{homedir}/bin
mv %{_builddir}%{homedir}/bin/extra/embedded-db-viewer.sh %{_builddir}%{homedir}/bin
# We don't really need any of these things.
rm -rf %{_builddir}%{homedir}/bin/extra
rm -f %{_builddir}%{homedir}/bin/*.bat
rm -rf %{_builddir}%{homedir}/resources/nativeAuth/osx-ppc
rm -rf %{_builddir}%{homedir}/resources/nativeAuth/win32-x86
rm -f %{_builddir}%{homedir}/lib/*.dll

%clean
rm -rf %{_builddir}

%preun
if [ "$1" == "0" ]; then
	# This is an uninstall, instead of an upgrade.
	/sbin/chkconfig --del openfire
	[ -x "/etc/init.d/openfire" ] && /etc/init.d/openfire stop
fi
# Force a happy exit even if openfire shutdown script didn't exit cleanly.
exit 0

%post
chown -R daemon:daemon %{homedir}
if [ "$1" == "1" ]; then
	# This is a fresh install, instead of an upgrade.
	/sbin/chkconfig --add openfire
fi

# Trigger a restart.
[ -x "/etc/init.d/openfire" ] && /etc/init.d/openfire condrestart

# Force a happy exit even if openfire condrestart script didn't exit cleanly.
exit 0

%files
%defattr(-,daemon,daemon)
%attr(750, daemon, daemon) %dir %{homedir}
%dir %{homedir}/bin
%{homedir}/bin/openfire.sh
%{homedir}/bin/openfirectl
%config(noreplace) %{homedir}/bin/embedded-db.rc
%{homedir}/bin/embedded-db-viewer.sh
%dir %{homedir}/conf
%config(noreplace) %{homedir}/conf/openfire.xml
%config(noreplace) %{homedir}/conf/security.xml
%config(noreplace) %{homedir}/conf/crowd.properties
%dir %{homedir}/lib
%{homedir}/lib/*.jar
%config(noreplace) %{homedir}/lib/log4j2.xml
%dir %{homedir}/logs
%dir %{homedir}/plugins
%{homedir}/plugins/search.jar
%dir %{homedir}/plugins/admin
%{homedir}/plugins/admin/*
%dir %{homedir}/resources
%dir %{homedir}/resources/database
%{homedir}/resources/database/*.sql
%dir %{homedir}/resources/database/upgrade
%dir %{homedir}/resources/database/upgrade/*
%{homedir}/resources/database/upgrade/*/*
%dir %{homedir}/resources/i18n
%{homedir}/resources/i18n/*
%dir %{homedir}/resources/nativeAuth
%dir %{homedir}/resources/nativeAuth/linux-i386
%{homedir}/resources/nativeAuth/linux-i386/*
%dir %{homedir}/resources/security
%dir %{homedir}/resources/spank
%{homedir}/resources/spank/index.html
%dir %{homedir}/resources/spank/WEB-INF
%{homedir}/resources/spank/WEB-INF/web.xml
%config(noreplace) %{homedir}/resources/security/keystore
%config(noreplace) %{homedir}/resources/security/truststore
%config(noreplace) %{homedir}/resources/security/client.truststore
%doc %{homedir}/documentation
%doc %{homedir}/LICENSE.html 
%doc %{homedir}/README.html 
%doc %{homedir}/changelog.html
%{_sysconfdir}/init.d/openfire
%config(noreplace) %{_sysconfdir}/sysconfig/openfire
%ifnarch noarch
%{homedir}/jre
%endif

%changelog
* Tue May 23 2023 Igniterealtime Community <webmaster@igniterealtime.org> 
- Build of version %{version} - changes here https://github.com/igniterealtime/Openfire/releases/tag/v%{version}
