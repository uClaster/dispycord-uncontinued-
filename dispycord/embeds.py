from typing import List, Dict, Any, Optional


class Embed:
    
    def __init__(
        self,
        *,
        description: str,
        title: str,
    ):
        
        self._raw: List[Dict[str, Any]] = [{
            'title': title,
            'description': description
        }]
        
    def add_field(
        self,
        *,
        name: str,
        value: str,
        inline: bool = False
    ) -> None:
        
        if not self._raw[0].get('fields'):
            self._raw[0]['fields'] = []
            
        self._raw[0]['fields'].append({
            'name': name,
            'value': value,
            'inline': inline
        })   
        
    def set_footer(
        self,
        *,
        text: str,
        icon_url: Optional[str] = None,
        proxy_icon_url: Optional[str] = None
    ) -> None:
        
        raw = {'text': text}
        
        if icon_url:
            raw['icon_url'] = icon_url
            
        print(raw)    
        
        self._raw[0]['footer'] = raw
        
    @property
    def to_dict(self):
        return self._raw