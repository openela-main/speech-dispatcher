%global _hardened_build 1

Name:          speech-dispatcher
Version:       0.10.2
Release:       4%{?dist}
Summary:       To provide a high-level device independent layer for speech synthesis

# Almost all files are under GPLv2+, however 
# src/c/clients/spdsend/spdsend.h is licensed under GPLv2,
# which makes %%_bindir/spdsend GPLv2.
License:       GPLv2+ and LGPLv2
URL:           http://devel.freebsoft.org/speechd
Source0:       https://github.com/brailcom/speechd/releases/download/%{version}/speech-dispatcher-%{version}.tar.gz
Source1:       http://www.freebsoft.org/pub/projects/sound-icons/sound-icons-0.1.tar.gz

Patch1:        0001-Remove-pyxdg-dependency.patch

BuildRequires: make
BuildRequires: alsa-lib-devel
BuildRequires: desktop-file-utils
BuildRequires: dotconf-devel
BuildRequires: espeak-ng-devel
BuildRequires: flite-devel
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: git-core
Buildrequires: glib2-devel
Buildrequires: intltool
Buildrequires: libao-devel
Buildrequires: libtool-ltdl-devel
Buildrequires: libsndfile-devel
Buildrequires: pulseaudio-libs-devel
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: systemd
BuildRequires: texinfo
BuildRequires: /usr/bin/help2man

Requires:      speech-dispatcher-espeak-ng
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Obsoletes:     speech-dispatcher-baratinoo < 0.9.1
Obsoletes:     speech-dispatcher-kali < 0.9.1

%description
* Common interface to different TTS engines
* Handling concurrent synthesis requests – requests may come
  asynchronously from multiple sources within an application
  and/or from more different applications.
* Subsequent serialization, resolution of conflicts and
  priorities of incoming requests
* Context switching – state is maintained for each client
  connection independently, event for connections from
  within one application.
* High-level client interfaces for popular programming languages
* Common sound output handling – audio playback is handled by
  Speech Dispatcher rather than the TTS engine, since most engines
  have limited sound output capabilities.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{_isa} = %{version}-%{release}
License:        GPLv2+

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package doc
Summary:        Documentation for speech-dispatcher
License:        GPLv2+
Requires:       %{name} = %{version}-%{release}
BuildArch: noarch

%description doc
speechd documentation

%package utils
Summary:        Various utilities for speech-dispatcher
License:        GPLv2+
Requires:       %{name}%{_isa} = %{version}-%{release}
Requires:       python3-speechd = %{version}-%{release}

%description utils
Various utilities for speechd

%package espeak-ng
Summary:        Speech Dispatcher espeak-ng module
Requires:       %{name}%{_isa} = %{version}-%{release}

%description espeak-ng
This package contains the espeak-ng output module for Speech Dispatcher.

%package festival
Summary:        Speech Dispatcher festival module
Requires:       %{name}%{_isa} = %{version}-%{release}
Requires:       festival-freebsoft-utils

%description festival
This package contains the festival output module for Speech Dispatcher.

%package flite
Summary:        Speech Dispatcher flite module
Requires:       %{name}%{_isa} = %{version}-%{release}

%description flite
This package contains the flite output module for Speech Dispatcher.

%package -n python3-speechd
Summary:        Python 3 Client API for speech-dispatcher
License:        GPLv2+
Requires:       %{name}%{_isa} = %{version}-%{release}

%description -n python3-speechd
Python 3 module for speech-dispatcher

%prep
%autosetup -S git

tar xf %{SOURCE1}

%build
%configure --disable-static \
	--with-alsa --with-pulse --with-libao \
	--with-flite --with-espeak-ng \
	--without-oss --without-nas --without-espeak \
	--with-kali=no --with-baratinoo=no --with-ibmtts=no --with-voxin=no \
	--sysconfdir=%{_sysconfdir} --with-default-audio-method=pulse

%make_build

%install
%make_install

install -p -m 0644 sound-icons-0.1/* %{buildroot}%{_datadir}/sounds/%{name}/

%find_lang speech-dispatcher

#Remove %{_infodir}/dir file
rm -f %{buildroot}%{_infodir}/dir

find %{buildroot} -name '*.la' -delete

# Move the config files from /usr/share to /etc
mkdir -p %{buildroot}%{_sysconfdir}/speech-dispatcher/clients
mkdir -p %{buildroot}%{_sysconfdir}/speech-dispatcher/modules
mv %{buildroot}%{_datadir}/speech-dispatcher/conf/speechd.conf %{buildroot}%{_sysconfdir}/speech-dispatcher/
mv %{buildroot}%{_datadir}/speech-dispatcher/conf/clients/* %{buildroot}%{_sysconfdir}/speech-dispatcher/clients
mv %{buildroot}%{_datadir}/speech-dispatcher/conf/modules/* %{buildroot}%{_sysconfdir}/speech-dispatcher/modules

# Create log dir
mkdir -p -m 0700 %{buildroot}%{_localstatedir}/log/speech-dispatcher/

# Verify the desktop files
desktop-file-validate %{buildroot}/%{_datadir}/speech-dispatcher/conf/desktop/speechd.desktop

# enable pulseaudio as default with a fallback to alsa
sed 's/# AudioOutputMethod "pulse,alsa"/AudioOutputMethod "pulse,alsa"/' %{buildroot}%{_sysconfdir}/speech-dispatcher/speechd.conf

%post 
%systemd_post speech-dispatcherd.service

%postun
%systemd_postun_with_restart speech-dispatcherd.service

%preun
%systemd_preun speech-dispatcherd.service

%files -f speech-dispatcher.lang
%license COPYING.LGPL
%doc NEWS README.md
%dir %{_sysconfdir}/speech-dispatcher/
%dir %{_sysconfdir}/speech-dispatcher/clients
%dir %{_sysconfdir}/speech-dispatcher/modules
%config(noreplace) %{_sysconfdir}/speech-dispatcher/speechd.conf
%config(noreplace) %{_sysconfdir}/speech-dispatcher/clients/*.conf
%config(noreplace) %{_sysconfdir}/speech-dispatcher/modules/*.conf
%exclude %{_sysconfdir}/speech-dispatcher/modules/espeak*.conf
%exclude %{_sysconfdir}/speech-dispatcher/modules/festival.conf
%exclude %{_sysconfdir}/speech-dispatcher/modules/flite.conf
%{_bindir}/speech-dispatcher
%{_datadir}/speech-dispatcher/
%{_libdir}/libspeechd.so.2
%{_libdir}/libspeechd.so.2.6.0
%dir %{_libdir}/speech-dispatcher-modules/
%{_libdir}/speech-dispatcher-modules/sd_cicero
%{_libdir}/speech-dispatcher-modules/sd_dummy
%{_libdir}/speech-dispatcher-modules/sd_generic
%dir %{_libdir}/speech-dispatcher
%{_libdir}/speech-dispatcher/spd*.so
%{_datadir}/sounds/speech-dispatcher
%{_mandir}/man1/speech-dispatcher.1*
%dir %attr(0700, root, root) %{_localstatedir}/log/speech-dispatcher/
%{_unitdir}/speech-dispatcherd.service

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc

%files doc
%{_infodir}/*

%files utils
%{_bindir}/spd-conf
%{_bindir}/spd-say
%{_bindir}/spdsend
%{_mandir}/man1/spd-conf.1*
%{_mandir}/man1/spd-say.1*

%files espeak-ng
%config(noreplace) %{_sysconfdir}/speech-dispatcher/modules/espeak-ng.conf
%{_libdir}/speech-dispatcher-modules/sd_espeak-ng

%files festival
%config(noreplace) %{_sysconfdir}/speech-dispatcher/modules/festival.conf
%{_libdir}/speech-dispatcher-modules/sd_festival

%files flite
%config(noreplace) %{_sysconfdir}/speech-dispatcher/modules/flite.conf
%{_libdir}/speech-dispatcher-modules/sd_flite

%files -n python3-speechd
%{python3_sitearch}/speechd*

%changelog
* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 0.10.2-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.10.2-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Nov 25 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 0.10.2-1
- Update to 0.10.2

* Fri Sep 11 2020 Kalev Lember <klember@redhat.com> - 0.10.1-2
- Fix crash with python 3.9 (#1878276)

* Mon Aug 10 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 0.10.1-1
- Update to 0.10.1

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-7
- Rebuilt for Python 3.9

* Tue Feb 25 2020 Than Ngo <than@redhat.com> - 0.9.1-6
- Fixed FTBFS

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-4
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-3
- Rebuilt for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri May 10 2019 Peter Robinson <pbrobinson@fedoraproject.org> 0.9.1-1
- speech-dispatcher 0.9.1

* Tue Feb 12 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.9.0-4
- Remove obsolete scriptlets

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jan 29 2019 Kalev Lember <klember@redhat.com> - 0.9.0-2
- Split new baratinoo and kali modules out into separate subpackages
- Install man pages
- Update the source URL

* Sun Jan 27 2019 Peter Robinson <pbrobinson@fedoraproject.org> 0.9.0-1
- speech-dispatcher 0.9.0

* Fri Jul 20 2018 Bastien Nocera <bnocera@redhat.com> - 0.8.8-8
- speech-dispatcher-0.8.8-8
- Remove pyxdg dependency

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.8-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.8.8-6
- Rebuilt for Python 3.7

* Thu Mar 08 2018 Ondřej Lysoněk <olysonek@redhat.com> - 0.8.8-5
- Make espeak-ng the default output module, drop the espeak output module

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 29 2018 Ondřej Lysoněk <olysonek@redhat.com> - 0.8.8-3
- Add support for espeak-ng, add speech-dispatcher-espeak-ng subpackage

* Thu Jan 25 2018 Rex Dieter <rdieter@fedoraproject.org> - 0.8.8-2
- include translations, pkgconfig support (#1538715)
- own %%_datadir/speech-dispatcher (#1480893)

* Tue Nov  7 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.8-1
- 0.8.8

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 16 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.7-1
- 0.8.7

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.8.6-2
- Rebuild for Python 3.6

* Wed Dec  7 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.6-1
- 0.8.6

* Wed Aug 10 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.5-1
- 0.8.5

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.4-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Apr 20 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.4-1
- 0.8.4

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.3-1
- 0.8.3

* Mon May 18 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.2-5
- Add missing libsndfile dependency to fix sound icon support

* Tue Apr 14 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.2-4
- Always install the espeak plugin

* Fri Mar 20 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.2-3
- Fix noarch docs Requires

* Fri Mar 20 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.2-2
- Use %%license
- Make packaging more modular (rhbz #799140)

* Fri Mar 20 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.2-1
- 0.8.2

* Mon Sep 29 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.1-1
- 0.8.1
- Split utils into sub package

* Fri Aug 29 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.8.1-0.1rc1
- 0.8.1 rc1
- Enable hardened build

* Thu Aug 21 2014 Kevin Fenzi <kevin@scrye.com> - 0.8-11
- Rebuild for rpm bug 1131960

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Kalev Lember <kalevlember@gmail.com> - 0.8-8
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Thu Mar 27 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.8-7
- Rebuild

* Fri Nov  1 2013 Matthias Clasen <mclasen@redhat.com> 0.8-6
- Avoid a crash in the festival module (#995639)

* Tue Aug 13 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.8-5
- Install clients as not longer installed by default (fixes RHBZ 996337)

* Sat Aug 10 2013 Rex Dieter <rdieter@fedoraproject.org> 0.8-4
- include/install missing headers

* Wed Aug  7 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.8-3
- Drop libao and python2 bindings

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 28 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.8-1
- Update to 0.8 stable release
- Rename python package for consistency
- Add python3 bindings - fixes RHBZ 867958
- Update the systemd scriptlets to the macroized versions

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Nov 29 2012 Bastien Nocera <bnocera@redhat.com> 0.7.1-9
- Move RPM hacks to source patches

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild
