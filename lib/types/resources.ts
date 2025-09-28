export interface ResourceLink {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  service: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface ResourceLinkGroup {
  user_id: string;
  user_email: string;
  user_name: string;
  links: ResourceLink[];
}

export interface ResourceLinkRequest {
  user_id: string;
  links: {
    service: string;
    url: string;
  }[];
}

