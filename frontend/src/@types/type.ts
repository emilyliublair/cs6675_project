export interface Post {
  _id?: string;
  title: string;
  description: string;
  name: string;
  publishDate: Date;
}

export interface Answer {
  title: string;
  description: string;
}
