-- DropForeignKey
ALTER TABLE "UsersArticles" DROP CONSTRAINT "UsersArticles_user_id_fkey";

-- AddForeignKey
ALTER TABLE "UsersArticles" ADD CONSTRAINT "UsersArticles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
