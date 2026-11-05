# Role: Linux AFD Postcode Install | ansible-collection-infrastructure
| Category | Author(s) |
|----------|--------|
| Linux & Storage | [charris-CH](https://github.com/charris-CH) |

&nbsp;

Installs the AFD Postcode Lookup application on a linux server and populates the `/opt/pcplus/data` directory with the most current data available.

&nbsp;

Mount points are defined per host group in [group_vars](../../group_vars/)

&nbsp;

Variable                    |Default  | Description
----------------------------|:-------:|------------
`storage_debugging_enabled` |`false`  | Enables debug output of resolved devices
