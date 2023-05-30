/*
  Warnings:

  - Added the required column `interval` to the `RssEntries` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "RssEntries" ADD COLUMN     "interval" INTEGER NOT NULL;
