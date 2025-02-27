export default interface User {
  id: string
  created_at_seconds: number
  avatar_url: string | null
  profile_pic: string,
  display_name?: string
}
