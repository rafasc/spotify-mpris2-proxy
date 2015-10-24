# spotify-mpris2-proxy

Currently Spotify doesn't implement the MPRIS D-Bus Interface according
with the spec (link below). As a consequence the KDE mediacontroller
plasmoid fails to recognize Spotify as mpris2 compliant player.

This is a "fake player" that implements* the mpris interface and relays
the commands to spotify.

  - http://specifications.freedesktop.org/mpris-spec/2.2/
  - https://projects.kde.org/projects/kde/workspace/plasma-workspace/

* This player doesn't follow the spec either but it's better than
nothing and good enough for KDE mediacontroller detect as a player and
provide basic controls.

This is just a workaround and is not intended as a final solution.

I hope spotify fix their implementation and make this program
irrelevant.
