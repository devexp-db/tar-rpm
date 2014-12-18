%if %{?WITH_SELINUX:0}%{!?WITH_SELINUX:1}
%global WITH_SELINUX 1
%endif

%global gitrev          5a9ac
%global tarballver      1.28

Summary: A GNU file archiving program (git version)
Name: tar-git-vanilla

# Note that there is no really sane way to version this pre-release packages,
# because we don't know the next version.
Version: 1.28.0.1
Release: 1git%{gitrev}%{?dist}
License: GPLv3+
Group: Applications/Archiving
URL: http://www.gnu.org/software/tar/

Source: tar-%{tarballver}.tar.gz

Patch0: 0001-testsuite-sort-otherwise-random-expected-output.patch

# run "make check" by default
%bcond_without check

BuildRequires: autoconf automake texinfo gettext libacl-devel rsh

%if %{with check}
# cover needs of tar's testsuite
BuildRequires: attr acl policycoreutils
%endif

%if %{WITH_SELINUX}
BuildRequires: libselinux-devel
%endif
Provides: bundled(gnulib)
Provides: /bin/tar
Provides: /bin/gtar
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description
The GNU tar program saves many files together in one archive and can
restore individual files (or all of the files) from that archive. Tar
can also be used to add supplemental files to an archive and to update
or list files in the archive. Tar includes multivolume support,
automatic archive compression/decompression, the ability to perform
remote archives, and the ability to perform incremental and full
backups.

If you want to use tar for remote backups, you also need to install
the rmt package on the remote box.

%prep
%setup -q -n tar-%{tarballver}
%patch0 -p1

%build
%if ! %{WITH_SELINUX}
%global CONFIGURE_SELINUX --without-selinux
%endif

%configure %{?CONFIGURE_SELINUX} \
    --with-lzma="xz --format=lzma" \
    DEFAULT_RMT_DIR=%{_sysconfdir} \
    RSH=/usr/bin/ssh
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

# XXX Nuke unpackaged files.
rm -f $RPM_BUILD_ROOT/%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/rmt
rm -f $RPM_BUILD_ROOT%{_libexecdir}/tar/pt_chown
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/rmt.*

mv $RPM_BUILD_ROOT/%{_bindir}/tar $RPM_BUILD_ROOT/%_bindir/%{name}
mv $RPM_BUILD_ROOT/%{_mandir}/man1/tar.1 $RPM_BUILD_ROOT/%{_mandir}/man1/%{name}.1
mv $RPM_BUILD_ROOT/%{_infodir}/tar.info-1 $RPM_BUILD_ROOT/%{_infodir}/%{name}.info-1
mv $RPM_BUILD_ROOT/%{_infodir}/tar.info-2 $RPM_BUILD_ROOT/%{_infodir}/%{name}.info-2
mv $RPM_BUILD_ROOT/%{_infodir}/tar.info $RPM_BUILD_ROOT/%{_infodir}/%{name}.info
rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale

%check
%if %{with check}
rm -f $RPM_BUILD_ROOT/test/testsuite
make check || TESTSUITEFLAGS=-v make check
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f %{_infodir}/%name.info.gz ]; then
   /sbin/install-info %{_infodir}/%name.info.gz %{_infodir}/dir || :
fi

%preun
if [ $1 = 0 ]; then
   if [ -f %{_infodir}/%name.info.gz ]; then
      /sbin/install-info --delete %{_infodir}/%name.info.gz %{_infodir}/dir || :
   fi
fi

%files
%doc AUTHORS ChangeLog ChangeLog.1 COPYING NEWS README THANKS TODO
%{_bindir}/%name
%{_mandir}/man1/%name.1*
%{_infodir}/%name.info*

%changelog
* Thu Dec 18 2014 Pavel Raiskup <praiskup@redhat.com> - 1.28.0.1-1git5a9ac
- latest HEAD rebase

* Wed Jul 16 2014 Pavel Raiskup <praiskup@redhat.com> - 1.27.90-2
- bump release and remove patch (causing non-vanilla-ness)

* Tue Jul 15 2014 Pavel Raiskup <praiskup@redhat.com> - 1.27.90-1
- initial packaging based on fedora-rawhide
