import pandas as pd
import partridge as ptg
import zipfile
import gtfstk
from constants import *
from aggregations import generate_trip_stats_aggregation, generate_route_stats_aggregation


def get_zones_df(local_tariff_zip_path):
    # not a true csv, so we need to jiggle it a bit, hence the 'EXTRA' field
    tariff_cols = ['ShareCode', 'ShareCodeDesc', 'ZoneCodes', 'Daily', 'Weekly', 'Monthly', 'FromDate', 'ToDate',
                   'EXTRA']
    reform_cols = ['StationId', 'ReformZoneCode', 'FromDate', 'ToDate', 'EXTRA']
    with zipfile.ZipFile(local_tariff_zip_path) as zf:
        tariff_df = (pd.read_csv(zf.open(TARIFF_TXT_NAME), header=None, skiprows=[0], names=tariff_cols)
                     .drop(columns=['EXTRA']))
        reform_df = (pd.read_csv(zf.open(TARIFF_TO_REFORM_ZONE), header=None, skiprows=[0], names=reform_cols)
                     .drop(columns=['EXTRA']))

    # remove ShareCodes which contain multiple zones  e.g. גוש דן מורחב
    tariff_df = (tariff_df[~ tariff_df.ZoneCodes.str.contains(';')]
                 .rename(columns={'ShareCodeDesc': 'zone_name',
                                  'ZoneCodes': 'zone_id'}))
    rs = reform_df[['StationId', 'ReformZoneCode']].drop_duplicates().applymap(str).set_index('StationId').iloc[:, 0]

    ts = (tariff_df[['zone_id', 'zone_name']].drop_duplicates().set_index('zone_id').iloc[:, 0])
    zones = rs.map(ts).reset_index().rename(columns={'StationId': 'stop_code', 'ReformZoneCode': 'zone_name'})
    return zones


def get_partridge_feed_by_date(zip_path, date):
    service_ids_by_date = ptg.read_service_ids_by_date(zip_path)  # , encoding='utf-8')
    service_ids = service_ids_by_date[date]

    feed = ptg.feed(zip_path, view={
        'trips.txt': {
            'service_id': service_ids,
        },
    },
                    # encoding='utf-8' # CUSTOM VERSION, NOT YET PUSHED
                    )
    return feed


def write_filtered_feed_by_date(zip_path, date, output_path):
    service_ids_by_date = ptg.read_service_ids_by_date(zip_path)  # , encoding='utf-8')
    service_ids = service_ids_by_date[date]

    ptg.writers.extract_feed(zip_path, output_path, {
        'trips.txt': {
            'service_id': service_ids,
        },
    })


def compute_trip_stats(feed, zones, date_str, file):
    """
    :param feed: Partridge feed
    :param zones: DataFrame with stop_code to zone_name mapping
    :param date: The original schedule date
    :param gtfs_file_name: The original GTFS (zip) file name
    :returns: A DataFrame with columns as described below

    Trip stats table has the following columns:

    - ``agency_id`` - Agency identifier, as specified in `agency.txt` file.
    - ``agency_name`` - The full name of the agency, as specified in `agency.txt` file.
    - ``all_stop_code`` - All stop codes (as specified in `stops.txt` file), separated by semicolons.
    - ``all_stop_desc_city`` - The city of the last stop of the trip (as described in `stop_desc` field in `stops.txt` \
        file), separated by semicolons.
    - ``all_stop_id`` - All stop identifiers (as specified in `stops.txt` file), separated by \
        semicolons.
    - ``all_stop_latlon`` - All stop waypoints (`stop_lat` and `stop_lon` as specified in `stops.txt` file), formatted \
        as `lat,lon` and separated by semicolons.
    - ``date`` - The original schedule date
    - ``direction_id`` - Indicates the direction of travel for a trip, as specified in `trips.txt` file.
    - ``distance`` - The full travel distance of the trip, which is the maximal \
        `shape_dist_traveled`, as specified in `stop_times.txt` file.
    - ``duration`` - Duration of the trip in hours
    - ``end_stop_city`` - The city of the last stop of the trip, as described in `stop_desc` field in `stops.txt` file.
    - ``end_stop_code`` - Stop code of the last stop of the trip
    - ``end_stop_desc`` - The description of the last stop of the trip, as described as `stop_desc` field in \
        `stops.txt` file.
    - ``end_stop_id`` - Stop ID of the last stop of the trip
    - ``end_stop_lat`` - Latitude of the last stop of the trip
    - ``end_stop_lon`` - Longitude of the last stop of the trip
    - ``end_stop_name`` - Stop name of the last stop of the trip
    - ``end_time`` - Last departure time of the trip
    - ``end_zone`` - Zone name of the last stop of the trip
    - ``gtfs_file_name`` - The original GTFS (zip) file name
    - ``is_loop`` - 1 if the start and end stop are less than 400m apart, otherwise 0
    - ``num_stops`` - Number of stops in trip
    - ``num_zones`` - Number of zones where the trip stops are. Zones are defined in the files in `Tariff.zip`.
    - ``num_zones_missing`` - Number of stops whose identifier is missing from the files in `Tariff.zip`.
    - ``route_alternative`` - A route's alternative identifier. Constructs a route identifier together \
        with ``route_direction`` and ``route_mkt``.
    - ``route_direction`` - A route's direction identifier. Constructs a route identifier together \
        with ``route_alternative`` and ``route_mkt``.
    - ``route_id`` - Route identifier, as specified in `routes.txt` file.
    - ``route_long_name`` - The full name of a route, as specified in `routes.txt` file.
    - ``route_mkt`` - MOT Line's 5-digit catalog number ("`מק"ט`"), a unique number at the line level, \
        but not unique at the alternative level. Constructs a route identifier together \
        with ``route_direction`` and ``route_alternative``.
    - ``route_short_name`` - The short name of a route, as specified in `routes.txt` file.
    - ``route_type`` - The type of transportation used on a route, as specified in \
        `routes.txt`. In Israel, MOT uses:
        * 0 for light train (Jerusalem Light Rail)
        * 2 for train (Israel Railways)
        * 3 for bus
        * 715 for Flexible Service Line ("קו בשירות גמיש")
    - ``shape_id`` - Shape identifier, as specified in `shapes.txt` file.
    - ``speed`` - Average speed of the trip (calculated as `distance/duration`)
    - ``start_stop_city`` - The city of the first stop of the trip, as specified in `stop_desc` field in `stops.txt` \
        file.
    - ``start_stop_code`` - Stop code of the first stop of the trip
    - ``start_stop_desc`` - The description of the first stop of the trip, as described as `stop_desc` field in \
        `stops.txt` file.
    - ``start_stop_id`` - Stop ID of the first stop of the trip
    - ``start_stop_lat`` - Latitude of the first stop of the trip
    - ``start_stop_lon`` - Longitude of the first stop of the trip
    - ``start_stop_name`` - Stop name of the first stop of the trip
    - ``start_time`` - First departure time of the trip
    - ``start_zone`` - Zone name of the first stop of the trip
    - ``trip_id`` - Trip identifier, as specified in `trips.txt` file.
    """

    f = feed.trips
    f = (f[['route_id', 'trip_id', 'direction_id', 'shape_id']]
         .merge(feed.routes[['route_id', 'route_short_name', 'route_long_name',
                             'route_type', 'agency_id', 'route_desc']])
         .merge(feed.agency[['agency_id', 'agency_name']], how='left', on='agency_id')
         .merge(feed.stop_times)
         .merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'stop_code', 'stop_desc']])
         .merge(zones, how='left')
         .sort_values(['trip_id', 'stop_sequence'])
         )

    # parse route_desc
    f[['route_mkt', 'route_direction', 'route_alternative']] = f['route_desc'].str.split('-', expand=True)
    f = f.drop('route_desc', axis=1)

    # parse stop_desc
    stop_desc_fields = {'street': 'רחוב',
                        'city': 'עיר',
                        'platform': 'רציף',
                        'floor': 'קומה'}

    stop_desc_prefix = 'stop_desc_'

    STOP_DESC_RE = ''
    for n, fld in stop_desc_fields.items():
        STOP_DESC_RE += fld + f':(?P<{stop_desc_prefix + n}>.*)'

    sd = f.stop_desc.str.extract(STOP_DESC_RE).apply(lambda x: x.str.strip())
    f = pd.concat([f, sd], axis=1)


    g = f.groupby('trip_id')
    aggregation = generate_trip_stats_aggregation(feed)
    h = g.apply(aggregation)
    h['distance'] = g.shape_dist_traveled.max()

    # Reset index and compute final stats
    h = h.reset_index()
    h['speed'] = h['distance'] / h['duration'] / 1000
    h[['start_time', 'end_time']] = (
        h[['start_time', 'end_time']].applymap(
            lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))
    )

    h['date'] = date_str
    h['date'] = pd.Categorical(h['date'])
    h['gtfs_file_name'] = file

    return h


def compute_route_stats_base_partridge(trip_stats_subset,
                                       date_str,
                                       file,
                                       headway_start_time='07:00:00',
                                       headway_end_time='19:00:00',
                                       *,
                                       split_directions=False):
    """
    Compute stats for the given subset of trips stats.

    Parameters
    ----------
    trip_stats_subset : DataFrame
        Subset of the output of :func:`.trips.compute_trip_stats`
    split_directions : boolean
        If ``True``, then separate the stats by trip direction (0 or 1);
        otherwise aggregate trips visiting from both directions.
        Default: ``False``
    headway_start_time : string
        HH:MM:SS time string indicating the start time for computing
        headway stats
        Default: ``'07:00:00'``
    headway_end_time : string
        HH:MM:SS time string indicating the end time for computing
        headway stats.
        Default: ``'19:00:00'``

    Returns
    -------
    DataFrame
        Columns are

        - ``route_id``
        - ``route_short_name``
        - ``agency_id``
        - ``agency_name``
        - ``route_long_name``
        - ``route_type``
        - ``direction_id`` - 1/0
        - ``num_trips`` - number of trips on the route in the subset
        - ``num_trip_starts`` - number of trips on the route with
          nonnull start times
        - ``num_trip_ends`` - number of trips on the route with nonnull
          end times that end before 23:59:59
        - ``is_loop`` - 1 if at least one of the trips on the route has
          its ``is_loop`` field equal to 1; 0 otherwise
        - ``is_bidirectional`` - 1 if the route has trips in both
          directions; 0 otherwise
        - ``start_time`` - start time of the earliest trip on the route
        - ``end_time`` - end time of latest trip on the route
        - ``max_headway`` - maximum of the durations (in minutes)
          between trip starts on the route between
          ``headway_start_time`` and ``headway_end_time`` on the given
          dates
        - ``min_headway`` - minimum of the durations (in minutes)
          mentioned above
        - ``mean_headway`` - mean of the durations (in minutes)
          mentioned above
        - ``peak_num_trips`` - maximum number of simultaneous trips in
          service (for the given direction, or for both directions when
          ``split_directions==False``)
        - ``peak_start_time`` - start time of first longest period
          during which the peak number of trips occurs
        - ``peak_end_time`` - end time of first longest period during
          which the peak number of trips occurs
        - ``service_duration`` - total of the duration of each trip on
          the route in the given subset of trips; measured in hours
        - ``service_distance`` - total of the distance traveled by each
          trip on the route in the given subset of trips; measured in
          whatever distance units are present in ``trip_stats_subset``;
          contains all ``np.nan`` entries if ``feed.shapes is None``
        - ``service_speed`` - service_distance/service_duration;
          measured in distance units per hour
        - ``mean_trip_distance`` - service_distance/num_trips
        - ``mean_trip_duration`` - service_duration/num_trips
        - ``start_stop_id`` - ``start_stop_id`` of the first trip for the route
        - ``end_stop_id`` - ``end_stop_id`` of the first trip for the route
        - ``start_stop_lat`` - ``start_stop_lat`` of the first trip for the route
        - ``start_stop_lon`` - ``start_stop_lon`` of the first trip for the route
        - ``end_stop_lat`` - ``end_stop_lat`` of the first trip for the route
        - ``end_stop_lon`` - ``end_stop_lon`` of the first trip for the route
        - ``num_stops`` - ``num_stops`` of the first trip for the route
        - ``start_zone`` - ``start_zone`` of the first trip for the route
        - ``end_zone`` - ``end_zone`` of the first trip for the route
        - ``num_zones`` -  ``num_zones`` of the first trip for the route
        - ``num_zones_missing`` -  ``num_zones_missing`` of the first trip for the route

        TODO: actually implement split_directions
        If not ``split_directions``, then remove the
        direction_id column and compute each route's stats,
        except for headways, using
        its trips running in both directions.
        In this case, (1) compute max headway by taking the max of the
        max headways in both directions; (2) compute mean headway by
        taking the weighted mean of the mean headways in both
        directions.

        If ``trip_stats_subset`` is empty, return an empty DataFrame.

    """
    f = trip_stats_subset.copy()
    f[['start_time', 'end_time']] = f[['start_time', 'end_time']].applymap(gtfstk.helpers.timestr_to_seconds)


    aggregation = generate_route_stats_aggregation(headway_start_time, headway_end_time)
    g = f.groupby('route_id').apply(aggregation).reset_index()

    # Compute a few more stats
    g['service_speed'] = g['service_distance'] / g['service_duration']
    g['mean_trip_distance'] = g['service_distance'] / g['num_trips']
    g['mean_trip_duration'] = g['service_duration'] / g['num_trips']

    # Convert route times to time strings
    time_cols = ['start_time', 'end_time', 'peak_start_time', 'peak_end_time']
    g[time_cols] = g[time_cols].applymap(lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))

    g['service_speed'] = g.service_speed / 1000

    g = g[['route_id', 'route_short_name', 'agency_id', 'agency_name',
           'route_long_name', 'route_type', 'route_mkt', 'route_direction', 'route_alternative',
           'num_trips', 'num_trip_starts',
           'num_trip_ends', 'is_loop', 'is_bidirectional', 'start_time',
           'end_time', 'max_headway', 'min_headway', 'mean_headway',
           'peak_num_trips', 'peak_start_time', 'peak_end_time',
           'service_distance', 'service_duration', 'service_speed',
           'mean_trip_distance', 'mean_trip_duration', 'start_stop_id',
           'end_stop_id', 'start_stop_name', 'end_stop_name',
           'start_stop_city', 'end_stop_city',
           'start_stop_desc', 'end_stop_desc',
           'start_stop_lat', 'start_stop_lon', 'end_stop_lat',
           'end_stop_lon', 'num_stops', 'start_zone', 'end_zone',
           'num_zones', 'num_zones_missing',
           'all_stop_latlon', 'all_stop_code', 'all_stop_id', 'all_stop_desc_city', 'all_start_time', 'all_trip_id',
           ]]

    g['date'] = date_str
    g['date'] = pd.Categorical(g['date'])
    g['gtfs_file_name'] = file


    return g
