export interface Post {
  _id: string;
  name: string;
  title: string;
  description: string;
  publishDate: string;
  answer?: string;
}

export interface Answer {
  _id: string;
  title: string;
  description: string;
  publishDate: string;
  upvotes: number;
  downvotes: number;
  edited?: boolean;
  editedBy?: string;
  editDate?: string;
  relevant_documents?: string[];
}
