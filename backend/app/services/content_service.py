from typing import List, Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        self.base_url = "https://api.tvmaze.com"
        self.cache_ttl = 86400  # 24 hours cache for content

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to TVMaze API with retry logic"""
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10)
        )
        async def _request():
            url = f"{self.base_url}/{endpoint}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        try:
            return await _request()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                logger.warning("Rate limit exceeded for TVMaze API")
                raise Exception("Rate limit exceeded. Please try again later.")
            raise

    async def search_content(
        self,
        query: str,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """Search for content"""
        if not query or len(query.strip()) < 2:
            return {
                "results": [],
                "page": page,
                "total_pages": 0,
                "total_results": 0
            }

        cache_key = f"search:{query}:{content_type or 'all'}:{language or 'all'}:{page}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # TVMaze search endpoint
            response = await self._make_request("search/shows", {"q": query})
            
            if not response:
                return {
                    "results": [],
                    "page": page,
                    "total_pages": 0,
                    "total_results": 0
                }
            
            # Process results
            processed_results = []
            for result in response:
                show = result.get("show", {})
                if not show:
                    continue

                # Filter by content type if specified
                if content_type:
                    show_type = show.get("type", "").lower()
                    if content_type.lower() not in show_type:
                        continue

                # Get language from the show data
                show_language = show.get("language", "").lower()
                
                # Filter by language if specified
                if language and show_language != language.lower():
                    continue

                summary = show.get("summary", "")
                overview = summary.replace("<p>", "").replace("</p>", "") if summary else ""
                image = show.get("image", {}) or {}
                
                processed_result = {
                    "id": show.get("id"),
                    "title": show.get("name"),
                    "overview": overview,
                    "poster_url": image.get("medium", ""),
                    "backdrop_url": image.get("original", ""),
                    "release_date": show.get("premiered"),
                    "rating": show.get("rating", {}).get("average"),
                    "genres": show.get("genres", []),
                    "status": show.get("status"),
                    "runtime": show.get("runtime"),
                    "type": show.get("type", "").lower(),
                    "language": show_language
                }
                
                if all(key in processed_result for key in ["id", "title"]):
                    processed_results.append(processed_result)
            
            # Create response with pagination info
            response_data = {
                "results": processed_results,
                "page": page,
                "total_pages": 1 if processed_results else 0,
                "total_results": len(processed_results)
            }
            
            # Cache the results
            if processed_results:
                await redis_service.set_cached_data(cache_key, response_data, ttl=3600)  # 1 hour cache for search results
            
            return response_data
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            raise

    async def get_content_by_id(self, tvmaze_id: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed content information by TVMaze ID"""
        cache_key = f"content:{content_type}:{tvmaze_id}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self._make_request(f"shows/{tvmaze_id}")
            
            # Process response
            processed_content = {
                "id": response.get("id"),
                "title": response.get("name"),
                "overview": response.get("summary", "").replace("<p>", "").replace("</p>", ""),
                "poster_url": response.get("image", {}).get("medium"),
                "backdrop_url": response.get("image", {}).get("original"),
                "release_date": response.get("premiered"),
                "rating": response.get("rating", {}).get("average"),
                "genres": response.get("genres", []),
                "status": response.get("status"),
                "runtime": response.get("runtime"),
                "type": "tv",
                "network": response.get("network", {}).get("name"),
                "schedule": response.get("schedule", {}),
                "web_channel": response.get("webChannel", {}).get("name"),
                "externals": response.get("externals", {}),
                "updated": response.get("updated")
            }
            
            # Cache the content
            await redis_service.set_cached_data(cache_key, processed_content, ttl=self.cache_ttl)
            return processed_content
        except Exception as e:
            logger.error(f"Error getting content by ID: {str(e)}")
            raise

    async def get_cast_and_crew(self, tvmaze_id: str, content_type: str) -> Dict[str, Any]:
        """Get cast and crew information for content"""
        cache_key = f"credits:{content_type}:{tvmaze_id}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self._make_request(f"shows/{tvmaze_id}/cast")
            
            # Process cast and crew
            cast = []
            crew = []
            
            for person in response:
                character = person.get("character", {})
                person_data = person.get("person", {})
                
                cast_member = {
                    "id": person_data.get("id"),
                    "name": person_data.get("name"),
                    "character": character.get("name"),
                    "profile_url": person_data.get("image", {}).get("medium")
                }
                cast.append(cast_member)
            
            # TVMaze doesn't provide separate crew information
            result = {
                "cast": cast,
                "crew": crew
            }
            
            # Cache the credits
            await redis_service.set_cached_data(cache_key, result, ttl=self.cache_ttl)
            return result
        except Exception as e:
            logger.error(f"Error getting cast and crew: {str(e)}")
            raise

    async def get_similar_content(self, tvmaze_id: str, content_type: str, page: int = 1) -> Dict[str, Any]:
        """Get similar content recommendations"""
        cache_key = f"similar:{content_type}:{tvmaze_id}:{page}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # Get the show's genres first
            show = await self.get_content_by_id(tvmaze_id, content_type)
            if not show:
                return {"results": [], "page": 1, "total_pages": 1, "total_results": 0}
            
            # Search for shows with similar genres
            genres = show.get("genres", [])
            if not genres:
                return {"results": [], "page": 1, "total_pages": 1, "total_results": 0}
            
            # Get shows with the same primary genre
            response = await self._make_request("shows", {"genres": genres[0]})
            
            # Filter out the current show and process results
            processed_results = []
            for result in response:
                if str(result.get("id")) != str(tvmaze_id):
                    processed_result = {
                        "id": result.get("id"),
                        "title": result.get("name"),
                        "overview": result.get("summary", "").replace("<p>", "").replace("</p>", ""),
                        "poster_url": result.get("image", {}).get("medium"),
                        "backdrop_url": result.get("image", {}).get("original"),
                        "release_date": result.get("premiered"),
                        "rating": result.get("rating", {}).get("average"),
                        "genres": result.get("genres", []),
                        "status": result.get("status"),
                        "runtime": result.get("runtime"),
                        "type": "tv"
                    }
                    processed_results.append(processed_result)
            
            # Create response with pagination info
            response_data = {
                "results": processed_results,
                "page": page,
                "total_pages": 1,  # TVMaze doesn't provide pagination
                "total_results": len(processed_results)
            }
            
            # Cache the results
            await redis_service.set_cached_data(cache_key, response_data, ttl=3600)  # 1 hour cache for similar content
            return response_data
        except Exception as e:
            logger.error(f"Error getting similar content: {str(e)}")
            raise

    async def get_trending_content(self, content_type: str = "all", time_window: str = "day") -> List[Dict[str, Any]]:
        """Get trending content"""
        cache_key = f"trending:{content_type}:{time_window}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # TVMaze doesn't have a trending endpoint, so we'll get shows sorted by rating
            response = await self._make_request("shows", {"sort": "rating"})
            
            # Process results
            processed_results = []
            for result in response[:20]:  # Limit to top 20
                processed_result = {
                    "id": result.get("id"),
                    "title": result.get("name"),
                    "overview": result.get("summary", "").replace("<p>", "").replace("</p>", ""),
                    "poster_url": result.get("image", {}).get("medium"),
                    "backdrop_url": result.get("image", {}).get("original"),
                    "release_date": result.get("premiered"),
                    "rating": result.get("rating", {}).get("average"),
                    "genres": result.get("genres", []),
                    "status": result.get("status"),
                    "runtime": result.get("runtime"),
                    "type": "tv"
                }
                processed_results.append(processed_result)
            
            # Cache the results
            await redis_service.set_cached_data(cache_key, processed_results, ttl=3600)  # 1 hour cache for trending
            return processed_results
        except Exception as e:
            logger.error(f"Error getting trending content: {str(e)}")
            raise

    async def get_genres(self, content_type: str) -> List[Dict[str, Any]]:
        """Get available genres for content type"""
        cache_key = f"genres:{content_type}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # TVMaze doesn't have a genres endpoint, so we'll get genres from shows
            response = await self._make_request("shows")
            
            # Extract unique genres
            genres = set()
            for show in response:
                genres.update(show.get("genres", []))
            
            # Convert to list of dictionaries
            genres_list = [{"id": i, "name": genre} for i, genre in enumerate(sorted(genres))]
            
            # Cache the genres
            await redis_service.set_cached_data(cache_key, genres_list, ttl=86400)  # 24 hours cache for genres
            return genres_list
        except Exception as e:
            logger.error(f"Error getting genres: {str(e)}")
            raise

    async def clear_content_cache(self, tvmaze_id: Optional[str] = None) -> None:
        """Clear content cache for a specific ID or all content"""
        if tvmaze_id:
            await redis_service.delete_cached_data(f"content:*:{tvmaze_id}")
        else:
            # Clear all content-related cache
            keys = await redis_service.redis.keys("content:*")
            if keys:
                await redis_service.redis.delete(*keys)

    async def get_show_details(self, show_id: int) -> Dict[str, Any]:
        """Get detailed information about a show"""
        try:
            # Get main show info
            show = await self._make_request(f"shows/{show_id}")
            if not show:
                return None

            # Get episodes
            episodes = await self._make_request(f"shows/{show_id}/episodes")
            
            # Get cast
            cast = await self._make_request(f"shows/{show_id}/cast")
            
            # Get crew
            crew = await self._make_request(f"shows/{show_id}/crew")
            
            # Get AKAs (alternate names)
            akas = await self._make_request(f"shows/{show_id}/akas")
            
            # Get images
            images = await self._make_request(f"shows/{show_id}/images")
            
            # Get seasons
            seasons = await self._make_request(f"shows/{show_id}/seasons")
            
            # Process episodes by season
            episodes_by_season = {}
            if episodes:
                for episode in episodes:
                    season = episode.get('season')
                    if season not in episodes_by_season:
                        episodes_by_season[season] = []
                    episodes_by_season[season].append(episode)

            return {
                "id": show.get("id"),
                "title": show.get("name"),
                "type": show.get("type"),
                "language": show.get("language"),
                "genres": show.get("genres", []),
                "status": show.get("status"),
                "runtime": show.get("runtime"),
                "premiered": show.get("premiered"),
                "ended": show.get("ended"),
                "rating": show.get("rating", {}).get("average"),
                "network": show.get("network", {}).get("name"),
                "webChannel": show.get("webChannel", {}).get("name"),
                "overview": show.get("summary", "").replace("<p>", "").replace("</p>", ""),
                "schedule": show.get("schedule", {}),
                "episodes": episodes_by_season,
                "cast": [
                    {
                        "person": {
                            "id": c.get("person", {}).get("id"),
                            "name": c.get("person", {}).get("name"),
                            "image": c.get("person", {}).get("image", {}).get("medium"),
                        },
                        "character": {
                            "id": c.get("character", {}).get("id"),
                            "name": c.get("character", {}).get("name"),
                        },
                    }
                    for c in cast or []
                ],
                "crew": [
                    {
                        "person": {
                            "id": c.get("person", {}).get("id"),
                            "name": c.get("person", {}).get("name"),
                            "image": c.get("person", {}).get("image", {}).get("medium"),
                        },
                        "type": c.get("type"),
                    }
                    for c in crew or []
                ],
                "alternateNames": [
                    {
                        "name": aka.get("name"),
                        "country": aka.get("country", {}).get("name"),
                    }
                    for aka in akas or []
                ],
                "images": [
                    {
                        "id": img.get("id"),
                        "type": img.get("type"),
                        "url": img.get("resolutions", {}).get("original", {}).get("url"),
                    }
                    for img in images or []
                ],
                "seasons": [
                    {
                        "id": s.get("id"),
                        "number": s.get("number"),
                        "episodeOrder": s.get("episodeOrder"),
                        "premiereDate": s.get("premiereDate"),
                        "endDate": s.get("endDate"),
                    }
                    for s in seasons or []
                ],
            }
        except Exception as e:
            logger.error(f"Error getting show details: {str(e)}")
            raise

    async def get_schedule(self, country: str = "US", date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get TV schedule for a specific country and date"""
        try:
            params = {"country": country}
            if date:
                params["date"] = date

            schedule = await self._make_request("schedule", params)
            
            if not schedule:
                return []

            return [
                {
                    "id": s.get("id"),
                    "airtime": s.get("airtime"),
                    "airstamp": s.get("airstamp"),
                    "runtime": s.get("runtime"),
                    "show": {
                        "id": s.get("show", {}).get("id"),
                        "name": s.get("show", {}).get("name"),
                        "type": s.get("show", {}).get("type"),
                        "language": s.get("show", {}).get("language"),
                        "status": s.get("show", {}).get("status"),
                        "image": s.get("show", {}).get("image", {}).get("medium"),
                    },
                }
                for s in schedule
            ]
        except Exception as e:
            logger.error(f"Error getting schedule: {str(e)}")
            raise

    async def search_people(self, query: str) -> List[Dict[str, Any]]:
        """Search for people by name"""
        try:
            people = await self._make_request("search/people", {"q": query})
            
            if not people:
                return []

            return [
                {
                    "id": p.get("person", {}).get("id"),
                    "name": p.get("person", {}).get("name"),
                    "image": p.get("person", {}).get("image", {}).get("medium"),
                    "birthday": p.get("person", {}).get("birthday"),
                    "deathday": p.get("person", {}).get("deathday"),
                    "gender": p.get("person", {}).get("gender"),
                    "country": p.get("person", {}).get("country", {}).get("name"),
                }
                for p in people
            ]
        except Exception as e:
            logger.error(f"Error searching people: {str(e)}")
            raise

    async def get_person_details(self, person_id: int) -> Dict[str, Any]:
        """Get detailed information about a person"""
        try:
            # Get main person info
            person = await self._make_request(f"people/{person_id}")
            
            # Get cast credits
            cast_credits = await self._make_request(f"people/{person_id}/castcredits?embed=show")
            
            # Get crew credits
            crew_credits = await self._make_request(f"people/{person_id}/crewcredits?embed=show")

            return {
                "id": person.get("id"),
                "name": person.get("name"),
                "image": person.get("image", {}).get("original"),
                "gender": person.get("gender"),
                "birthday": person.get("birthday"),
                "deathday": person.get("deathday"),
                "country": person.get("country", {}).get("name"),
                "castRoles": [
                    {
                        "character": c.get("character", {}).get("name"),
                        "show": {
                            "id": c.get("_embedded", {}).get("show", {}).get("id"),
                            "name": c.get("_embedded", {}).get("show", {}).get("name"),
                            "image": c.get("_embedded", {}).get("show", {}).get("image", {}).get("medium"),
                        }
                    }
                    for c in cast_credits or []
                ],
                "crewRoles": [
                    {
                        "type": c.get("type"),
                        "show": {
                            "id": c.get("_embedded", {}).get("show", {}).get("id"),
                            "name": c.get("_embedded", {}).get("show", {}).get("name"),
                            "image": c.get("_embedded", {}).get("show", {}).get("image", {}).get("medium"),
                        }
                    }
                    for c in crew_credits or []
                ]
            }
        except Exception as e:
            logger.error(f"Error getting person details: {str(e)}")
            raise

    async def get_episode_details(self, episode_id: int) -> Dict[str, Any]:
        """Get detailed information about an episode"""
        try:
            episode = await self._make_request(f"episodes/{episode_id}?embed[]=guestcast&embed[]=guestcrew")
            if not episode:
                return None

            return {
                "id": episode.get("id"),
                "name": episode.get("name"),
                "season": episode.get("season"),
                "number": episode.get("number"),
                "airdate": episode.get("airdate"),
                "airtime": episode.get("airtime"),
                "runtime": episode.get("runtime"),
                "rating": episode.get("rating", {}).get("average"),
                "image": episode.get("image", {}).get("original"),
                "summary": episode.get("summary", "").replace("<p>", "").replace("</p>", ""),
                "guestCast": [
                    {
                        "person": {
                            "id": c.get("person", {}).get("id"),
                            "name": c.get("person", {}).get("name"),
                            "image": c.get("person", {}).get("image", {}).get("medium"),
                        },
                        "character": {
                            "id": c.get("character", {}).get("id"),
                            "name": c.get("character", {}).get("name"),
                        },
                    }
                    for c in episode.get("_embedded", {}).get("guestcast", [])
                ],
                "guestCrew": [
                    {
                        "person": {
                            "id": c.get("person", {}).get("id"),
                            "name": c.get("person", {}).get("name"),
                            "image": c.get("person", {}).get("image", {}).get("medium"),
                        },
                        "type": c.get("type"),
                    }
                    for c in episode.get("_embedded", {}).get("guestcrew", [])
                ],
            }
        except Exception as e:
            logger.error(f"Error getting episode details: {str(e)}")
            raise

    async def get_show_by_external_id(self, external_id: str, source: str) -> Dict[str, Any]:
        """Look up a show by external ID (IMDb, TheTVDB, etc.)"""
        try:
            show = await self._make_request(f"lookup/shows?{source}={external_id}")
            if not show:
                return None

            return {
                "id": show.get("id"),
                "title": show.get("name"),
                "type": show.get("type"),
                "language": show.get("language"),
                "genres": show.get("genres", []),
                "status": show.get("status"),
                "runtime": show.get("runtime"),
                "premiered": show.get("premiered"),
                "rating": show.get("rating", {}).get("average"),
                "image": show.get("image", {}).get("original"),
                "summary": show.get("summary", "").replace("<p>", "").replace("</p>", ""),
            }
        except Exception as e:
            logger.error(f"Error looking up show by external ID: {str(e)}")
            raise

    async def get_show_updates(self, since: Optional[int] = None) -> Dict[str, Any]:
        """Get updates for shows since a specific timestamp"""
        try:
            params = {}
            if since:
                params["since"] = since

            updates = await self._make_request("updates/shows", params)
            return updates
        except Exception as e:
            logger.error(f"Error getting show updates: {str(e)}")
            raise

    async def get_person_updates(self, since: Optional[int] = None) -> Dict[str, Any]:
        """Get updates for people since a specific timestamp"""
        try:
            params = {}
            if since:
                params["since"] = since

            updates = await self._make_request("updates/people", params)
            return updates
        except Exception as e:
            logger.error(f"Error getting person updates: {str(e)}")
            raise

    async def get_web_schedule(self, date: Optional[str] = None, country: str = "US") -> List[Dict[str, Any]]:
        """Get web/streaming schedule"""
        try:
            params = {"country": country}
            if date:
                params["date"] = date

            schedule = await self._make_request("schedule/web", params)
            
            if not schedule:
                return []

            return [
                {
                    "id": s.get("id"),
                    "airtime": s.get("airtime"),
                    "airstamp": s.get("airstamp"),
                    "runtime": s.get("runtime"),
                    "show": {
                        "id": s.get("show", {}).get("id"),
                        "name": s.get("show", {}).get("name"),
                        "type": s.get("show", {}).get("type"),
                        "language": s.get("show", {}).get("language"),
                        "status": s.get("show", {}).get("status"),
                        "image": s.get("show", {}).get("image", {}).get("medium"),
                        "webChannel": s.get("show", {}).get("webChannel", {}).get("name"),
                    },
                }
                for s in schedule
            ]
        except Exception as e:
            logger.error(f"Error getting web schedule: {str(e)}")
            raise

    async def get_show_index(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get a paginated list of all shows"""
        try:
            shows = await self._make_request(f"shows?page={page}")
            
            if not shows:
                return []

            return [
                {
                    "id": s.get("id"),
                    "title": s.get("name"),
                    "type": s.get("type"),
                    "language": s.get("language"),
                    "genres": s.get("genres", []),
                    "status": s.get("status"),
                    "runtime": s.get("runtime"),
                    "premiered": s.get("premiered"),
                    "rating": s.get("rating", {}).get("average"),
                    "image": s.get("image", {}).get("medium"),
                }
                for s in shows
            ]
        except Exception as e:
            logger.error(f"Error getting show index: {str(e)}")
            raise

    async def get_people_index(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get a paginated list of all people"""
        try:
            people = await self._make_request(f"people?page={page}")
            
            if not people:
                return []

            return [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "image": p.get("image", {}).get("medium"),
                    "birthday": p.get("birthday"),
                    "deathday": p.get("deathday"),
                    "gender": p.get("gender"),
                    "country": p.get("country", {}).get("name"),
                }
                for p in people
            ]
        except Exception as e:
            logger.error(f"Error getting people index: {str(e)}")
            raise

content_service = ContentService()