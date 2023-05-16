-- CreateEnum
CREATE TYPE "Language" AS ENUM ('English', 'Dutch');

-- AlterTable
ALTER TABLE "NewsArticles" ADD COLUMN     "language" "Language" NOT NULL DEFAULT 'English';
