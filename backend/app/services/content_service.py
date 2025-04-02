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
        page: int = 1
    ) -> Dict[str, Any]:
        """Search for content"""
        cache_key = f"search:{query}:{content_type or 'all'}:{page}"
        
        # Try to get from cache first
        cached_data = await redis_service.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # TVMaze search endpoint
            response = await self._make_request("search/shows", {"q": query})
            
            # Process results
            processed_results = []
            for result in response:
                show = result.get("show", {})
                processed_result = {
                    "id": show.get("id"),
                    "title": show.get("name"),
                    "overview": show.get("summary", "").replace("<p>", "").replace("</p>", ""),
                    "poster_url": show.get("image", {}).get("medium"),
                    "backdrop_url": show.get("image", {}).get("original"),
                    "release_date": show.get("premiered"),
                    "rating": show.get("rating", {}).get("average"),
                    "genres": show.get("genres", []),
                    "status": show.get("status"),
                    "runtime": show.get("runtime"),
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

content_service = ContentService() 