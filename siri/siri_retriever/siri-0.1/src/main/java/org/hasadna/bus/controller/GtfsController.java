package org.hasadna.bus.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.hasadna.bus.entity.gtfs.Route;
import org.hasadna.bus.entity.gtfs.RouteSearchParams;
import org.hasadna.bus.entity.gtfs.Stop;
import org.hasadna.bus.service.SiriConsumeService;
import org.hasadna.bus.service.gtfs.ReadRoutesFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Profile;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@Profile("gtfs")
@RequestMapping("/gtfs")
public class GtfsController {


    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    @Autowired
    SiriConsumeService siriConsumeService;

    @Autowired
    ReadRoutesFile rrf;

    // returns details about lineref, including the line published name, and list of stopCodes for all its stops
    @RequestMapping(value="/line/ref/{lineRef}", method={RequestMethod.GET}, produces = "application/json")
    public Route retrieveLineRefDetails(@PathVariable String lineRef) {
        logger.info("line/ref/{} ", lineRef);
        Route route = rrf.findRouteById(lineRef);
        List<String> lastStops = rrf.findLastStopCodeByRouteId(route.routeId, true);
        route.lastStopCode = lastStops.toString();
        //route.weeklyDepartureTimes = rrf.findDeparturesByRouteId(route.routeId);
        return route;
    }

    @RequestMapping(value="/line/short/name/{publishedName}", method={RequestMethod.GET}, produces = "application/json")
    public Map<String, List<Route> > retrieveLineRefDetailsByPublishedName(@PathVariable String publishedName) {
        logger.info("line/short/name/{} ", publishedName);
        List<Route> list = rrf.findRouteByPublishedName(publishedName, Optional.empty());
        list.stream().
                map(route -> {
                    List<String> lastStops = rrf.findLastStopCodeByRouteId(route.routeId, true);
                    route.lastStopCode = lastStops.toString();
                    //route.weeklyDepartureTimes = rrf.findDeparturesByRouteId(route.routeId);
                    return route;
                }).
                collect(Collectors.toList());
        Map<String, List<Route> > groupedByMakat =
            list.stream().collect(Collectors.groupingBy(Route::getMakat));
        return groupedByMakat;
    }


//// use POST with body like this example:
//    {
//        "publishedName":"480",
//            "cityName":"תל אביב"
//    }
    @RequestMapping(value="/line/short/name/search", method={RequestMethod.POST}, produces = "application/json")
    public List<Route> retrieveLineRefDetailsByPublishedName(@RequestBody RouteSearchParams rsp) {
        logger.info("line/short/name/search {} {}", rsp.publishedName, rsp.cityName);
        List<Route> list = rrf.findRouteByPublishedName(rsp.publishedName, Optional.of(rsp.cityName));
        list = list.stream().
                map(route -> {
                    List<String> lastStops = rrf.findLastStopCodeByRouteId(route.routeId, true);
                    route.lastStopCode = lastStops.toString();
                    if (lastStops.size() == 1) {
                        route.lastStopCode = lastStops.get(0).toString();
                    }
                    //route.weeklyDepartureTimes = rrf.findDeparturesByRouteId(route.routeId);
                    return route;
                }).
                collect(Collectors.toList());
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            logger.info("request:{}", objectMapper.writeValueAsString(rsp));
            logger.info("response:{}", objectMapper.writeValueAsString(list));
            for (Route r : list) {
                String desc = "קו " + rsp.publishedName + " -- " + rsp.cityName + " " ;
                String lastStopCode = r.lastStopCode;
                String lineRef = r.routeId;
                String s = "\n                   {\"description\" : \"" + desc + "\",\n" +
                        "                    \"stopCode\" : \"" + lastStopCode + "\",\n" +
                        "                    \"previewInterval\" : \"PT1H\",\n" +
                        "                    \"lineRef\" : \"" + lineRef + "\",\n" +
                        "                    \"maxStopVisits\" : 7,\n" +
                        "                    \"executeEvery\" : 30}";
                logger.info(s);
            }
        }
        catch (Exception ex) {
            logger.error("absorbing unhandled", ex);
        }
        return list;
    }


    // return details about the specified stop (identified by its stopCode)
    @RequestMapping(value="/stop/details/code/{stopCode}", method={RequestMethod.GET}, produces = "application/json")
    public Stop retrieveStopDetails(@PathVariable String stopCode) {
        logger.info("stop/details/code/{} ", stopCode);
        Stop result = rrf.findStopByCode(stopCode);
        return result;
    }

    // return details about the specified stop (identified by its stopCode)
    @RequestMapping(value="/stop/details/id/{stopId}", method={RequestMethod.GET}, produces = "application/json")
    public Stop retrieveStopDetailsById(@PathVariable String stopId) {
        logger.info("stop/details/id/{} ", stopId);
        Stop result = rrf.findStopById(stopId);
        return result;
    }

}
