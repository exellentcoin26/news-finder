/*
  Warnings:

  - The primary key for the `UsersArticles` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `article_id` on the `UsersArticles` table. All the data in the column will be lost.
  - You are about to drop the column `url` on the `UsersArticles` table. All the data in the column will be lost.
  - Added the required column `source_url` to the `UsersArticles` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "UsersArticles" DROP CONSTRAINT "UsersArticles_article_id_url_fkey";

-- DropIndex
DROP INDEX "UsersArticles_article_id_url_key";

-- AlterTable
ALTER TABLE "NewsArticles" ADD COLUMN     "usersArticlesSource_id" INTEGER,
ADD COLUMN     "usersArticlesUser_id" INTEGER;

-- AlterTable
ALTER TABLE "UsersArticles" DROP CONSTRAINT "UsersArticles_pkey",
DROP COLUMN "article_id",
DROP COLUMN "url",
ADD COLUMN     "labels" TEXT[],
ADD COLUMN     "source_url" TEXT NOT NULL,
ADD CONSTRAINT "UsersArticles_pkey" PRIMARY KEY ("user_id", "source_id");

-- AddForeignKey
ALTER TABLE "NewsArticles" ADD CONSTRAINT "NewsArticles_usersArticlesUser_id_usersArticlesSource_id_fkey" FOREIGN KEY ("usersArticlesUser_id", "usersArticlesSource_id") REFERENCES "UsersArticles"("user_id", "source_id") ON DELETE SET NULL ON UPDATE CASCADE;
