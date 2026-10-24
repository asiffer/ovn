FROM debian:13-slim

RUN apt update -y && apt upgrade -y
RUN apt install -y ovn-common ovn-host ovn-central net-tools iproute2

# add ovn script to PATH
ENV PATH="${PATH}:/usr/share/ovn/scripts"


RUN mkdir -p /var/lib/ovn
RUN ovsdb-tool create /var/lib/ovn/ovnnb_db.db /usr/share/ovn/ovn-nb.ovsschema
RUN ovsdb-tool create /var/lib/ovn/ovnsb_db.db /usr/share/ovn/ovn-sb.ovsschema


COPY --chmod=755 run.sh /run.sh

CMD ["/run.sh"]
# expose the ovn northbound database (for management) and southbound database (for ovn-controllers)
EXPOSE 6641
EXPOSE 6642